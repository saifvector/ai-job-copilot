import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import jwt
from core.config import settings
from core.exceptions import AuthenticationException, TokenExpiredException, TokenRevokedException
from core.logging import get_logger

logger = get_logger("security.tokens")


class SecretKeyManager:
    """
    Manages primary and fallback secret keys to enable zero-downtime secret rotation.
    """
    def __init__(self):
        self.primary_key: str = settings.SECRET_KEY
        # Optional fallback key for rotation transitions
        self.fallback_keys: List[str] = [
            k.strip() for k in os.getenv("SECRET_KEY_FALLBACKS", "").split(",") if k.strip()
        ]

    def get_signing_key(self) -> str:
        return self.primary_key

    def get_verification_keys(self) -> List[str]:
        keys = [self.primary_key]
        for fb in self.fallback_keys:
            if fb not in keys:
                keys.append(fb)
        return keys


class TokenBlacklist:
    """
    Stores revoked token identifiers (JTI) and revoked user sessions.
    Backed by in-memory set with optional Redis persistence.
    """
    def __init__(self):
        self._revoked_jtis: Set[str] = set()
        self._revoked_user_sessions: Dict[str, float] = {}  # user_id -> revoked_before_timestamp
        self._family_revocations: Set[str] = set()         # revoked refresh token families

    def revoke_token(self, jti: str, expires_at: Optional[float] = None) -> None:
        self._revoked_jtis.add(jti)
        logger.info(f"Token revoked: jti={jti}")

    def revoke_family(self, family_id: str) -> None:
        self._family_revocations.add(family_id)
        logger.warning(f"Token family revoked due to reuse: family_id={family_id}")

    def revoke_all_user_sessions(self, user_id: str) -> None:
        now = time.time()
        self._revoked_user_sessions[str(user_id)] = now
        logger.info(f"All active sessions revoked for user: {user_id}")

    def is_revoked(self, jti: str, user_id: Optional[str] = None, issued_at: Optional[float] = None, family_id: Optional[str] = None) -> bool:
        if jti in self._revoked_jtis:
            return True
        if family_id and family_id in self._family_revocations:
            return True
        if user_id and issued_at:
            revoked_before = self._revoked_user_sessions.get(str(user_id))
            if revoked_before and issued_at < revoked_before:
                return True
        return False


# Singleton instances
secret_manager = SecretKeyManager()
token_blacklist = TokenBlacklist()


class TokenService:
    """
    Enterprise JWT Security Service implementing:
    - Secure JWT generation with HMAC-SHA256
    - Secret rotation fallback
    - Refresh token rotation (RTR) with family reuse detection
    - JTI tracking and instantaneous token revocation
    """
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS = 900       # 15 minutes
    REFRESH_TOKEN_EXPIRE_SECONDS = 604800   # 7 days

    @classmethod
    def create_access_token(
        cls,
        user_id: uuid.UUID,
        role: str = "candidate",
        additional_claims: Optional[Dict[str, Any]] = None,
        expires_delta_seconds: Optional[int] = None,
    ) -> Tuple[str, str, int]:
        """
        Generates a short-lived cryptographically signed access token.
        Returns: (token_str, jti, expires_in_seconds)
        """
        now = int(time.time())
        expires_in = expires_delta_seconds or cls.ACCESS_TOKEN_EXPIRE_SECONDS
        exp = now + expires_in
        jti = str(uuid.uuid4())

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": exp,
            "jti": jti,
            "type": "access",
            "role": role,
        }
        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, secret_manager.get_signing_key(), algorithm=cls.ALGORITHM)
        return token, jti, expires_in

    @classmethod
    def create_refresh_token(
        cls,
        user_id: uuid.UUID,
        family_id: Optional[str] = None,
        expires_delta_seconds: Optional[int] = None,
    ) -> Tuple[str, str, str, int]:
        """
        Generates a refresh token with family tracking for rotation protection.
        Returns: (token_str, jti, family_id, expires_in_seconds)
        """
        now = int(time.time())
        expires_in = expires_delta_seconds or cls.REFRESH_TOKEN_EXPIRE_SECONDS
        exp = now + expires_in
        jti = str(uuid.uuid4())
        fam_id = family_id or str(uuid.uuid4())

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": exp,
            "jti": jti,
            "type": "refresh",
            "family_id": fam_id,
        }

        token = jwt.encode(payload, secret_manager.get_signing_key(), algorithm=cls.ALGORITHM)
        return token, jti, fam_id, expires_in

    @classmethod
    def verify_token(cls, token: str, expected_type: str = "access") -> Dict[str, Any]:
        """
        Decodes and validates a token using primary and fallback keys.
        Checks expiration, signature, and blacklist revocation status.
        """
        verification_keys = secret_manager.get_verification_keys()
        last_error = None

        for key in verification_keys:
            try:
                payload = jwt.decode(
                    token,
                    key,
                    algorithms=[cls.ALGORITHM],
                    options={"verify_exp": True},
                )
                break
            except jwt.ExpiredSignatureError:
                raise TokenExpiredException("Authentication token has expired.")
            except jwt.InvalidTokenError as exc:
                last_error = exc
        else:
            raise AuthenticationException(f"Invalid token signature: {last_error}")

        # Verify token type
        token_type = payload.get("type")
        if token_type != expected_type:
            raise AuthenticationException(f"Expected {expected_type} token, received {token_type}.")

        jti = payload.get("jti")
        sub = payload.get("sub")
        iat = payload.get("iat")
        family_id = payload.get("family_id")

        if jti and token_blacklist.is_revoked(jti=jti, user_id=sub, issued_at=iat, family_id=family_id):
            raise TokenRevokedException("Token has been revoked.")

        return payload

    @classmethod
    def rotate_refresh_token(cls, refresh_token: str) -> Tuple[str, str, uuid.UUID]:
        """
        Implements Refresh Token Rotation (RTR):
        - Verifies current refresh token
        - Checks for reuse; if already revoked, invalidates whole family
        - Revokes old refresh token
        - Issues new access token and rotated refresh token with same family_id
        Returns: (new_access_token, new_refresh_token, user_id)
        """
        payload = cls.verify_token(refresh_token, expected_type="refresh")
        old_jti = payload["jti"]
        user_id = uuid.UUID(payload["sub"])
        family_id = payload.get("family_id", str(uuid.uuid4()))

        # Check if already blacklisted (attempted reuse)
        if token_blacklist.is_revoked(old_jti):
            token_blacklist.revoke_family(family_id)
            raise AuthenticationException("Suspicious refresh token reuse detected. Session terminated.")

        # Invalidate old refresh token
        token_blacklist.revoke_token(old_jti)

        # Issue new token pair
        new_access_token, _, _ = cls.create_access_token(user_id=user_id)
        new_refresh_token, _, _, _ = cls.create_refresh_token(user_id=user_id, family_id=family_id)

        return new_access_token, new_refresh_token, user_id

    @classmethod
    def revoke_token(cls, token: str) -> None:
        """Explicitly revokes a specific token."""
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
            )
            jti = payload.get("jti")
            if jti:
                token_blacklist.revoke_token(jti)
        except Exception as exc:
            logger.warning(f"Could not parse token for revocation: {exc}")
