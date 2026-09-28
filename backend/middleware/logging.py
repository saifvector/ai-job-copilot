import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from core.logging import get_logger

logger = get_logger("http.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured HTTP request/response logging middleware.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            # Skip noise on frequent simple root health probes
            if path != "/health" or response.status_code >= 400:
                logger.info(
                    f"{method} {path} - {response.status_code} ({duration_ms}ms) [client: {client_ip}]"
                )
            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"{method} {path} - FAILED with exception: {exc} ({duration_ms}ms) [client: {client_ip}]"
            )
            raise
