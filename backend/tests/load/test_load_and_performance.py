import asyncio
import time
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concurrent_api_latency_under_300ms(client: AsyncClient):
    """
    Performance test: Fires 20 concurrent requests to health probe
    and validates that 95th percentile latency is strictly under 300ms.
    """
    async def make_request():
        t0 = time.perf_counter()
        res = await client.get("/health")
        duration_ms = (time.perf_counter() - t0) * 1000
        return res.status_code, duration_ms

    # Concurrently execute 20 requests
    tasks = [make_request() for _ in range(20)]
    results = await asyncio.gather(*tasks)

    durations = [dur for code, dur in results if code == 200]
    assert len(durations) == 20

    durations.sort()
    p95 = durations[int(len(durations) * 0.95)]
    avg_duration = sum(durations) / len(durations)

    # API target: < 300ms
    assert p95 < 300.0, f"P95 latency was {p95}ms, exceeding 300ms target."
    assert avg_duration < 150.0, f"Average latency was {avg_duration}ms."


@pytest.mark.asyncio
async def test_metrics_performance_under_100ms(client: AsyncClient):
    """
    Validates metrics exposition endpoint generates responses in under 100ms.
    """
    t0 = time.perf_counter()
    res = await client.get("/metrics")
    latency = (time.perf_counter() - t0) * 1000

    assert res.status_code == 200
    assert latency < 100.0, f"Metrics generation took {latency}ms, exceeding 100ms."
