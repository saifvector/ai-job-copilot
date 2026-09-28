import hashlib
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from fastapi import Depends, Header, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db
from core.exceptions import AuthenticationError, AuthorizationError, RateLimitExceededError
from core.security.rate_limiter import SlidingWindowRateLimiter
from models.api_key import ApiKeyModel
from repositories.api_key_repository import ApiKeyRepository
from repositories.api_usage_log_repository import ApiUsageLogRepository

API_KEY_PREFIX = "ajc_live_"
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

# Global rate limiter for public API keys (60 req/min per key)
_api_key_rate_limiter = SlidingWindowRateLimiter(window_seconds=60)


class ApiKeyService:
    """
    Manages API key generation, cryptographic hashing, scope verification, and lifecycle.
    """

    @staticmethod
    def generate_key() -> Tuple[str, str, str]:
        """
        Generates a new secure API key.
        Returns: (raw_key, key_hash, prefix)
        """
        raw_token = secrets.token_urlsafe(32)
        raw_key = f"{API_KEY_PREFIX}{raw_token}"
        key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        # Prefix shows first 12 chars and last 4 chars, e.g. "ajc_live_ab...1234"
        prefix = f"{raw_key[:12]}...{raw_key[-4:]}"
        return raw_key, key_hash, prefix

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ApiKeyRepository(session)
        self.usage_repo = ApiUsageLogRepository(session)

    async def create_api_key(
        self,
        user_id: uuid.UUID,
        name: str,
        scopes: Optional[List[str]] = None,
        rate_limit: int = 60,
        monthly_limit: int = 10000,
        expires_in_days: Optional[int] = None,
    ) -> Tuple[ApiKeyModel, str]:
        raw_key, key_hash, prefix = self.generate_key()
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        default_scopes = ["read:profile", "read:resume", "read:matches", "read:applications", "read:reports"]
        assigned_scopes = scopes if scopes is not None else default_scopes

        key_model = ApiKeyModel(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            prefix=prefix,
            scopes=assigned_scopes,
            rate_limit=rate_limit,
            monthly_limit=monthly_limit,
            expires_at=expires_at,
            is_active=True,
        )
        saved = await self.repo.create(key_model)
        return saved, raw_key

    async def rotate_api_key(
        self,
        key_id: uuid.UUID,
        user_id: uuid.UUID,
        expires_in_days: Optional[int] = None,
    ) -> Tuple[ApiKeyModel, str]:
        old_key = await self.repo.get(key_id)
        if not old_key or old_key.user_id != user_id or not old_key.is_active:
            raise AuthenticationError("Active API key not found for rotation")

        # Deactivate previous key
        old_key.is_active = False
        old_key.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

        # Create new replacement key with identical name and scopes
        return await self.create_api_key(
            user_id=user_id,
            name=f"{old_key.name} (Rotated)",
            scopes=old_key.scopes,
            rate_limit=old_key.rate_limit,
            monthly_limit=old_key.monthly_limit,
            expires_in_days=expires_in_days,
        )

    async def validate_api_key(
        self,
        raw_key: str,
        required_scopes: Optional[List[str]] = None,
    ) -> ApiKeyModel:
        if not raw_key:
            raise AuthenticationError("API key missing. Provide X-API-Key or Bearer token.")

        key_hash = self.hash_key(raw_key.strip())
        key = await self.repo.find_by_key_hash(key_hash)

        if not key or not key.is_active:
            raise AuthenticationError("Invalid or revoked API key")

        if key.expires_at:
            exp = key.expires_at if key.expires_at.tzinfo is not None else key.expires_at.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                key.is_active = False
                await self.session.flush()
                raise AuthenticationError("API key has expired")

        # Scope validation
        if required_scopes:
            user_scopes = set(key.scopes or [])
            for required in required_scopes:
                if required not in user_scopes and "admin:all" not in user_scopes:
                    raise AuthorizationError(f"API key missing required scope: '{required}'")

        # Enforce rate limiting per API key
        rate_limit = key.rate_limit or 60
        allowed, rem, reset = _api_key_rate_limiter.is_allowed(
            key=f"apikey_{key.id}",
            limit=rate_limit,
            window=60,
        )
        if not allowed:
            raise RateLimitExceededError(
                f"API key rate limit exceeded. Max {rate_limit} requests/min. Reset in {reset}s"
            )

        # Update last used timestamp
        await self.repo.update_last_used(key.id)
        return key


class ApiKeyContext:
    def __init__(self, key: ApiKeyModel, start_time: float):
        self.key = key
        self.user_id = key.user_id
        self.key_id = key.id
        self.scopes = key.scopes
        self.start_time = start_time


def require_api_key(required_scopes: Optional[List[str]] = None):
    """
    FastAPI dependency factory enforcing API key authentication and scope authorization.
    Supports either 'X-API-Key' header or 'Authorization: Bearer ajc_live_...'
    """
    async def _dependency(
        request: Request,
        x_api_key: Optional[str] = Security(api_key_header_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> ApiKeyContext:
        start_time = time.perf_counter()
        raw_key = x_api_key

        if not raw_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token_candidate = auth_header[7:].strip()
                if token_candidate.startswith(API_KEY_PREFIX):
                    raw_key = token_candidate

        if not raw_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "API_KEY_MISSING", "message": "Missing API key in X-API-Key header"},
            )

        service = ApiKeyService(db)
        try:
            key_model = await service.validate_api_key(raw_key, required_scopes=required_scopes)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"code": "UNAUTHORIZED", "message": str(e)})
        except AuthorizationError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "FORBIDDEN", "message": str(e)})
        except RateLimitExceededError as e:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail={"code": "RATE_LIMIT_EXCEEDED", "message": str(e)})

        context = ApiKeyContext(key=key_model, start_time=start_time)
        # Attach to request state for timing / analytics logging
        request.state.api_key_context = context
        return context

    return _dependency
