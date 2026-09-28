import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""
    sub: str = Field(..., description="Subject identifier (user UUID)")
    exp: int = Field(..., description="Expiration timestamp (epoch seconds)")
    iat: int = Field(..., description="Issued at timestamp (epoch seconds)")
    jti: str = Field(..., description="Unique JWT token ID")
    type: str = Field(..., description="Token type: access or refresh")
    role: str = Field("candidate", description="User authorization role")
    family_id: Optional[str] = Field(None, description="Token rotation family ID")


class TokenResponse(BaseModel):
    """Response returned upon login or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration window in seconds")
    user_id: uuid.UUID


class RefreshTokenRequest(BaseModel):
    """Payload to exchange a refresh token for new access and rotated refresh tokens."""
    refresh_token: str = Field(..., description="Current active refresh token")


class RevokeTokenRequest(BaseModel):
    """Payload to explicitly revoke an active token or session."""
    token: Optional[str] = Field(None, description="Specific token to revoke; defaults to bearer header if omitted")
    revoke_all_sessions: bool = Field(False, description="Whether to revoke all active tokens for the user")


class SessionInfoResponse(BaseModel):
    """Active session diagnostic information."""
    user_id: uuid.UUID
    email: Optional[str] = None
    role: str = "candidate"
    token_id: str
    issued_at: datetime
    expires_at: datetime
    is_revoked: bool = False


class RateLimitStatusResponse(BaseModel):
    """Status returned by rate limiting instrumentation."""
    limit: int
    remaining: int
    reset_seconds: int
    client_ip: str


class FileValidationResult(BaseModel):
    """Result of secure upload and malware scan checks."""
    is_valid: bool
    filename: str
    mime_type: str
    size_bytes: int
    sha256_checksum: str
    is_quarantined: bool
    quarantine_path: Optional[str] = None
    malware_scan_clean: bool
    scan_engine: str
    error_message: Optional[str] = None
