import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, Request, status
from core.dependencies import get_audit_log_service, get_authenticated_user_id
from core.exceptions import AuthenticationException, BadRequestException
from core.security.tokens import TokenService, token_blacklist
from schemas.security import (
    RefreshTokenRequest,
    RevokeTokenRequest,
    SessionInfoResponse,
    TokenResponse,
)
from services.audit_log_service import AuditLogService

router = APIRouter(prefix="/auth", tags=["Security & Authentication"])


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Issue Access and Refresh Token Pair",
    description="Authenticates candidate identity and issues a short-lived JWT access token and rotated refresh token.",
)
async def login_for_access_token(
    request: Request,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    audit_service: AuditLogService = Depends(get_audit_log_service),
) -> TokenResponse:
    access_token, jti, expires_in = TokenService.create_access_token(user_id=user_id)
    refresh_token, _, _, _ = TokenService.create_refresh_token(user_id=user_id)

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    await audit_service.log_auth_event(
        user_id=user_id,
        event_name="AUTH_LOGIN",
        token_id=jti,
        ip_address=client_ip,
        user_agent=user_agent,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user_id=user_id,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate Refresh Token",
    description="Performs Refresh Token Rotation (RTR). Replaces active refresh token and issues a new access token.",
)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    audit_service: AuditLogService = Depends(get_audit_log_service),
) -> TokenResponse:
    new_access, new_refresh, user_id = TokenService.rotate_refresh_token(payload.refresh_token)

    await audit_service.log_auth_event(
        user_id=user_id,
        event_name="AUTH_TOKEN_ROTATED",
    )

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=TokenService.ACCESS_TOKEN_EXPIRE_SECONDS,
        user_id=user_id,
    )


@router.post(
    "/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke Token or Terminate Session",
    description="Adds token JTI to the revocation blacklist or revokes all active sessions for the user.",
)
async def revoke_token(
    payload: RevokeTokenRequest,
    request: Request,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    audit_service: AuditLogService = Depends(get_audit_log_service),
):
    token_to_revoke = payload.token
    if not token_to_revoke:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_to_revoke = auth_header[7:].strip()

    if token_to_revoke:
        TokenService.revoke_token(token_to_revoke)

    if payload.revoke_all_sessions:
        token_blacklist.revoke_all_user_sessions(str(user_id))

    await audit_service.log_auth_event(
        user_id=user_id,
        event_name="AUTH_TOKEN_REVOKED",
        details={"all_sessions": payload.revoke_all_sessions},
    )

    return {"success": True, "message": "Token / session revoked successfully."}


@router.get(
    "/session",
    response_model=SessionInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Inspect Active Session",
    description="Validates active JWT Bearer token and returns session metadata.",
)
async def get_current_session(
    request: Request,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
) -> SessionInfoResponse:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        # Dev demo session fallback
        return SessionInfoResponse(
            user_id=user_id,
            role="candidate",
            token_id="dev-demo-session",
            issued_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
            is_revoked=False,
        )

    token = auth_header[7:].strip()
    payload = TokenService.verify_token(token, expected_type="access")

    return SessionInfoResponse(
        user_id=user_id,
        role=payload.get("role", "candidate"),
        token_id=payload.get("jti", ""),
        issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        is_revoked=False,
    )
