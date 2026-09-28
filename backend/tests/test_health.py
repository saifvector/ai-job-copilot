import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoint(client: AsyncClient):
    """
    Test mandatory GET /health contract:
    Response: { "status": "healthy" }
    """
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "healthy"}


@pytest.mark.asyncio
async def test_v1_health_endpoint(client: AsyncClient):
    """
    Test detailed GET /api/v1/health endpoint.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "database" in data
    assert data["status"] in ["healthy", "degraded"]


@pytest.mark.asyncio
async def test_correlation_id_and_timing_headers(client: AsyncClient):
    """
    Test that custom middlewares inject tracking and timing headers.
    """
    response = await client.get("/health")
    assert "x-correlation-id" in response.headers
    assert "x-process-time" in response.headers
