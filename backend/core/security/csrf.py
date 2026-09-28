import hmac
import secrets
from typing import Optional, Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from core.exceptions import ForbiddenException
from core.logging import get_logger

logger = get_logger("security.csrf")

SAFE_METHODS: Set[str] = {"GET", "HEAD", "OPTIONS"}
CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "x-csrf-token"


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Double-submit cookie CSRF protection middleware.
    Exempts safe methods (GET, HEAD, OPTIONS) and requests authenticated via Bearer tokens.
    Requires matching X-CSRF-Token header when cookie-based requests mutate state.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Safe methods are always permitted
        if request.method in SAFE_METHODS:
            response = await call_next(request)
            # Ensure CSRF cookie is initialized if not present
            if CSRF_COOKIE_NAME not in request.cookies:
                token = secrets.token_hex(32)
                response.set_cookie(
                    key=CSRF_COOKIE_NAME,
                    value=token,
                    httponly=False,  # Client JS can read to place in header
                    samesite="lax",
                    secure=not request.url.hostname in ("localhost", "127.0.0.1"),
                )
            return response

        # Check if request is authenticated using stateless Authorization: Bearer, X-API-Key, or public endpoints
        auth_header = request.headers.get("Authorization", "")
        api_key_header = request.headers.get("X-API-Key", "")
        if auth_header.startswith("Bearer ") or api_key_header or request.url.path.startswith("/api/public/"):
            # Programmatic API requests are immune to cross-site cookie forgery
            return await call_next(request)

        # For cookie-based mutating requests, enforce double-submit CSRF token validation
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME) or request.headers.get("X-CSRF-Token")

        # If both are present, verify equality using timing-safe comparison
        if cookie_token and header_token:
            if not hmac.compare_digest(cookie_token, header_token):
                logger.warning(f"CSRF token mismatch detected on {request.url.path}")
                raise ForbiddenException("CSRF token verification failed.")
        elif cookie_token and not header_token:
            # Session cookie exists without CSRF header
            logger.warning(f"Missing CSRF header on cookie request to {request.url.path}")
            raise ForbiddenException("Missing CSRF token header.")

        return await call_next(request)
