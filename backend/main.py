from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.router import api_v1_router
from core.config import settings
from core.database import check_database_health, get_db_session, init_db
from core.dependencies import get_db
from core.jobs.scheduler import start_job_scheduler, stop_job_scheduler
from core.logging import get_logger, setup_logging
from middleware import (
    CorrelationIdMiddleware,
    RequestLoggingMiddleware,
    TimingMiddleware,
    register_exception_handlers,
)
from schemas.common import HealthStatusResponse

# Initialize structured logging
setup_logging()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle management (startup and graceful shutdown).
    """
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION} "
        f"[env={settings.ENVIRONMENT}, debug={settings.DEBUG}]"
    )
    # Check DB on startup
    db_health = await check_database_health()
    if db_health.get("connected"):
        logger.info(f"Database connected successfully ({db_health.get('latency_ms')}ms)")
        await init_db()
    else:
        logger.warning(f"Database not reachable on startup: {db_health.get('error')}")

    # Start 6-hour periodic job discovery scheduler
    start_job_scheduler()

    yield

    # Halt background scheduler gracefully
    stop_job_scheduler()
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")



def create_application() -> FastAPI:
    """
    FastAPI application factory.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "AI Job Copilot - Production backend API foundation.\n\n"
            "Provides identity, candidate profile storage, health telemetry, "
            "and robust async database persistence."
        ),
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 1. Register Global Exception Handlers
    register_exception_handlers(app)

    # 2. Register Custom Middleware (Order matters: execution is outside-in)
    from core.security import RateLimitMiddleware, CSRFProtectionMiddleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CSRFProtectionMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    # 3. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Correlation-ID", "X-User-Id", "X-CSRF-Token", "X-API-Key", "X-Webhook-Signature", "X-Webhook-Event", "Accept", "Origin"],
    )

    # 4. Mandatory Health Endpoints
    @app.get(
        "/health",
        tags=["Health & Diagnostics"],
        summary="Service Liveness & Aggregated Health Check",
        description="Fast root health probe for load balancers and orchestrators reporting overall system status.",
    )
    async def root_health(
        session: AsyncSession = Depends(get_db),
        detailed: bool = False,
    ):
        from core.cache import cache_manager
        from services.monitoring_service import MonitoringService
        from sqlalchemy import text
        import time

        start_time = time.perf_counter()
        db_connected = False
        db_latency = 0.0
        try:
            await session.execute(text("SELECT 1"))
            db_latency = round((time.perf_counter() - start_time) * 1000, 2)
            db_connected = True
        except Exception:
            db_latency = round((time.perf_counter() - start_time) * 1000, 2)

        cache_ok, cache_latency, engine_name = await cache_manager.ping()
        is_healthy = db_connected and cache_ok

        if not detailed:
            return {"status": "healthy" if is_healthy else "degraded"}

        mon = MonitoringService()
        return {
            "status": "healthy" if is_healthy else "degraded",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": mon.get_uptime_seconds(),
            "database": {
                "connected": db_connected,
                "latency_ms": db_latency,
                "status": "healthy" if db_connected else "unhealthy",
            },
            "cache": {
                "connected": cache_ok,
                "latency_ms": cache_latency,
                "engine": engine_name,
            },
        }

    @app.get(
        "/health/database",
        tags=["Health & Diagnostics"],
        summary="Database Connection & Pool Health",
        description="Detailed database probe measuring query latency, pool utilization, and migration status.",
    )
    async def database_health(
        session: AsyncSession = Depends(get_db),
    ):
        from services.database_health_service import DatabaseHealthService
        service = DatabaseHealthService(session)
        return await service.check_health()

    @app.get(
        "/health/cache",
        tags=["Health & Diagnostics"],
        summary="Redis Cache Health",
        description="Pings Redis/In-memory fallback cache and measures response latency and key counts.",
    )
    async def cache_health():
        from core.cache import cache_manager
        return await cache_manager.get_stats()

    @app.get(
        "/health/ai",
        tags=["Health & Diagnostics"],
        summary="AI Model & Provider Health",
        description="Audits Google Gemini API key configuration and AI orchestrator model readiness.",
    )
    async def ai_health():
        has_key = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5)
        return {
            "status": "healthy" if has_key else "degraded",
            "provider": "Google Gemini",
            "primary_model": settings.GEMINI_PRIMARY_MODEL,
            "fallback_model": settings.GEMINI_FALLBACK_MODEL,
            "api_key_configured": has_key,
            "request_timeout_seconds": settings.AI_REQUEST_TIMEOUT,
        }

    @app.get(
        "/metrics",
        tags=["Health & Diagnostics"],
        summary="Prometheus Observability Metrics",
        description="Plain text Prometheus exposition format for latency, error rates, AI consumption, and system telemetry.",
    )
    async def prometheus_metrics():
        from fastapi.responses import PlainTextResponse
        from services.monitoring_service import MonitoringService
        mon = MonitoringService()
        content = await mon.generate_prometheus_metrics()
        return PlainTextResponse(content=content, media_type="text/plain; version=0.0.4")

    # Root welcome / meta endpoint
    @app.get(
        "/",
        include_in_schema=False,
    )
    async def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
        }

    # 5. Versioned API Router & Public Platform API
    from api.public.v1 import public_v1_router
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
    app.include_router(public_v1_router, prefix="/api/public/v1")

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
