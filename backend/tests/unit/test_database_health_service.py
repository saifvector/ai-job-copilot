import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.database_health_service import DatabaseHealthService


@pytest.mark.asyncio
async def test_database_health_service_check_health(db_session: AsyncSession):
    service = DatabaseHealthService(session=db_session)
    health = await service.check_health()

    assert health["connected"] is True
    assert health["status"] in ("healthy", "degraded")
    assert health["latency_ms"] >= 0.0
    assert "pool" in health


@pytest.mark.asyncio
async def test_database_health_service_diagnostics(db_session: AsyncSession):
    service = DatabaseHealthService(session=db_session)
    diag = await service.run_diagnostics()

    assert "avg_query_latency_ms" in diag
    assert len(diag["sample_latencies_ms"]) == 3
    assert "table_record_counts" in diag


@pytest.mark.asyncio
async def test_database_health_service_migration_safety(db_session: AsyncSession):
    service = DatabaseHealthService(session=db_session)
    migration_status = await service.check_migration_safety()

    assert migration_status["is_safe"] is True
    assert migration_status["migrations_count"] >= 1
    assert "synced" in migration_status["status"]
