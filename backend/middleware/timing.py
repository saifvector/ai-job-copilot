import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

PROCESS_TIME_HEADER = "X-Process-Time"


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware appending request latency timing header (X-Process-Time) in seconds.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers[PROCESS_TIME_HEADER] = f"{process_time:.4f}s"

        # Record latency telemetry for MonitoringService
        try:
            from services.monitoring_service import metrics_collector
            metrics_collector.record_request(process_time * 1000, request.method)
        except Exception:
            pass

        return response
