from fastapi import APIRouter, status
from core.config import settings
from core.database import check_database_health
from schemas.common import DetailedHealthResponse, HealthStatusResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Detailed Health Check",
    description="Check backend API service, environment metadata, and database connection probe.",
)
async def detailed_health_check() -> DetailedHealthResponse:
    """Returns system status, active version, environment, and DB health check."""
    db_health = await check_database_health()
    overall_status = "healthy" if db_health.get("connected") else "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_health,
    )


@router.get(
    "/ping",
    response_model=HealthStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Ping",
)
async def ping() -> HealthStatusResponse:
    return HealthStatusResponse(status="healthy")
