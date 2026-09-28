import hmac
import hashlib
import secrets
from typing import Optional
from core.config import settings


def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure hexadecimal token."""
    return secrets.token_hex(length)


def constant_time_compare(val1: str, val2: str) -> bool:
    """Timing-attack resistant string comparison."""
    return hmac.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


def hash_secret(secret: str, salt: Optional[str] = None) -> str:
    """
    Produce a deterministic SHA-256 hash using the secret key salt.
    """
    salt_val = salt or settings.SECRET_KEY
    return hashlib.sha256(f"{salt_val}:{secret}".encode("utf-8")).hexdigest()
