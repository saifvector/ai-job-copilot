import asyncio
import pytest
from core.cache import InMemoryCache, RedisCacheManager


@pytest.mark.asyncio
async def test_in_memory_cache_set_get_and_expiration():
    cache = InMemoryCache()
    await cache.set("test_key", {"foo": "bar"}, ttl_seconds=1)

    val = await cache.get("test_key")
    assert val == {"foo": "bar"}

    # Wait for TTL expiration
    await asyncio.sleep(1.1)
    expired_val = await cache.get("test_key")
    assert expired_val is None


@pytest.mark.asyncio
async def test_cache_pattern_invalidation():
    cache = InMemoryCache()
    await cache.set("jobs:search:hash1", ["job1"])
    await cache.set("jobs:search:hash2", ["job2"])
    await cache.set("matches:job:123", {"score": 90})

    deleted = await cache.delete_pattern("jobs:search:*")
    assert deleted == 2

    # jobs cache gone, match cache intact
    assert await cache.get("jobs:search:hash1") is None
    assert await cache.get("matches:job:123") is not None


@pytest.mark.asyncio
async def test_redis_cache_manager_fallback():
    mgr = RedisCacheManager()
    mgr.use_fallback = True  # Explicitly force in-memory fallback for test determinism

    await mgr.set("analytics:user:demo", {"profile_score": 95}, ttl_seconds=60)
    data = await mgr.get("analytics:user:demo")
    assert data == {"profile_score": 95}

    deleted = await mgr.invalidate_user_analytics_cache("demo")
    assert deleted >= 1
    assert await mgr.get("analytics:user:demo") is None
