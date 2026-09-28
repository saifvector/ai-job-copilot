import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from core.config import settings
from core.logging import get_logger

logger = get_logger("core.cache")


class InMemoryCache:
    """
    High-performance in-memory cache with TTL expiration.
    Used as primary dev/test cache and as an automatic fallback if Redis is unavailable.
    """
    def __init__(self):
        self._store: Dict[str, Tuple[Any, float]] = {}  # key -> (data, expire_at)

    async def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        val, expire_at = self._store[key]
        if time.time() > expire_at:
            self._store.pop(key, None)
            return None
        return val

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        self._store[key] = (value, time.time() + ttl_seconds)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def delete_pattern(self, pattern: str) -> int:
        """Deletes keys matching a wildcard prefix pattern like 'jobs:search:*'."""
        prefix = pattern.rstrip("*")
        keys_to_del = [k for k in self._store.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            self._store.pop(k, None)
        return len(keys_to_del)

    async def ping(self) -> bool:
        return True

    async def key_count(self) -> int:
        # Prune expired before counting
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired:
            self._store.pop(k, None)
        return len(self._store)


class RedisCacheManager:
    """
    Enterprise Redis Cache Provider with transparent in-memory fallback.
    Caches:
    - Job search queries ('jobs:search:<hash>')
    - Match computation results ('matches:job:<user_id>:<job_id>')
    - Candidate dashboard analytics ('analytics:user:<user_id>')
    """
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._redis_client = None
        self._fallback = InMemoryCache()
        self.use_fallback = False
        self._initialized = False

    async def _get_client(self):
        if self.use_fallback:
            return None

        if self._redis_client is None and not self._initialized:
            self._initialized = True
            try:
                import redis.asyncio as aioredis
                self._redis_client = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=1.5,
                    socket_timeout=1.5,
                )
                await self._redis_client.ping()
                logger.info(f"Connected to Redis cache at {self.redis_url}")
            except Exception as exc:
                logger.warning(f"Redis unavailable ({exc}). Using in-memory fallback cache.")
                self.use_fallback = True
                self._redis_client = None

        return self._redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Fetches and deserializes value by key."""
        client = await self._get_client()
        if client:
            try:
                raw = await client.get(key)
                if raw is not None:
                    return json.loads(raw)
                return None
            except Exception as exc:
                logger.warning(f"Redis get failed for {key}: {exc}. Checking fallback.")
                return await self._fallback.get(key)
        return await self._fallback.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Serializes and sets value with TTL in seconds."""
        client = await self._get_client()
        if client:
            try:
                serialized = json.dumps(value, default=str)
                await client.setex(key, ttl_seconds, serialized)
                return
            except Exception as exc:
                logger.warning(f"Redis set failed for {key}: {exc}. Writing to fallback.")
                await self._fallback.set(key, value, ttl_seconds)
                return
        await self._fallback.set(key, value, ttl_seconds)

    async def delete(self, key: str) -> None:
        """Deletes a specific cache key."""
        client = await self._get_client()
        if client:
            try:
                await client.delete(key)
            except Exception as exc:
                logger.warning(f"Redis delete failed for {key}: {exc}")
        await self._fallback.delete(key)

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidates all keys matching a prefix or pattern."""
        deleted_count = 0
        client = await self._get_client()
        if client:
            try:
                keys = await client.keys(pattern)
                if keys:
                    deleted_count = await client.delete(*keys)
            except Exception as exc:
                logger.warning(f"Redis pattern invalidation failed for {pattern}: {exc}")
        fb_deleted = await self._fallback.delete_pattern(pattern)
        return max(deleted_count, fb_deleted)

    # Specific Domain Cache Invalidation Hooks
    async def invalidate_job_search_cache(self) -> int:
        return await self.invalidate_pattern("jobs:search:*")

    async def invalidate_user_match_cache(self, user_id: str) -> int:
        return await self.invalidate_pattern(f"matches:job:{user_id}:*")

    async def invalidate_user_analytics_cache(self, user_id: str) -> int:
        return await self.invalidate_pattern(f"analytics:user:{user_id}*")

    async def ping(self) -> Tuple[bool, float, str]:
        """Pings cache server and returns (connected, latency_ms, engine_name)."""
        start = time.perf_counter()
        client = await self._get_client()
        if client:
            try:
                await client.ping()
                latency = round((time.perf_counter() - start) * 1000, 2)
                return True, latency, "redis"
            except Exception:
                pass
        latency = round((time.perf_counter() - start) * 1000, 2)
        return True, latency, "in_memory_fallback"

    async def get_stats(self) -> Dict[str, Any]:
        """Returns health telemetry and metrics for monitoring."""
        connected, latency, engine_name = await self.ping()
        client = await self._get_client()
        key_count = 0
        used_memory = "N/A"
        if client:
            try:
                info = await client.info("memory")
                used_memory = info.get("used_memory_human", "N/A")
                dbsize = await client.dbsize()
                key_count = dbsize
            except Exception:
                pass
        else:
            key_count = await self._fallback.key_count()

        return {
            "connected": connected,
            "latency_ms": latency,
            "engine": engine_name,
            "active_keys": key_count,
            "used_memory_human": used_memory,
            "status": "healthy" if connected else "degraded",
        }


# Global cache singleton
cache_manager = RedisCacheManager()
