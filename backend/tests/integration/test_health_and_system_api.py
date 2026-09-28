import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health_endpoints(client: AsyncClient):
    # 1. GET /health (detailed=true)
    res = await client.get("/health?detailed=true")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert "cache" in data

    # Default liveness contract
    liveness = await client.get("/health")
    assert liveness.status_code == 200
    assert liveness.json()["status"] in ("healthy", "degraded")

    # 2. GET /health/database
    db_res = await client.get("/health/database")
    assert db_res.status_code == 200
    db_data = db_res.json()
    assert db_data["connected"] is True

    # 3. GET /health/cache
    cache_res = await client.get("/health/cache")
    assert cache_res.status_code == 200
    cache_data = cache_res.json()
    assert cache_data["connected"] is True

    # 4. GET /health/ai
    ai_res = await client.get("/health/ai")
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    assert ai_data["provider"] == "Google Gemini"


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(client: AsyncClient):
    res = await client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    text = res.text
    assert "job_copilot_uptime_seconds" in text
    assert "job_copilot_http_requests_total" in text


@pytest.mark.asyncio
async def test_system_metrics_and_ai_costs(client: AsyncClient):
    # Metrics
    res = await client.get("/api/v1/system/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "api_latency" in data
    assert "error_rates_by_category" in data

    # AI Costs
    cost_res = await client.get("/api/v1/system/ai-costs")
    assert cost_res.status_code == 200
    cost_data = cost_res.json()
    assert "total_tokens" in cost_data
    assert "by_model" in cost_data


@pytest.mark.asyncio
async def test_auth_token_issuance_and_refresh(client: AsyncClient):
    # 1. POST /api/v1/auth/token
    token_res = await client.post("/api/v1/auth/token")
    assert token_res.status_code == 200
    tokens = token_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # 2. GET /api/v1/auth/session with Bearer token
    session_res = await client.get(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert session_res.status_code == 200
    session_data = session_res.json()
    assert session_data["role"] == "candidate"

    # 3. POST /api/v1/auth/refresh
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert new_tokens["access_token"] != access_token

    # 4. POST /api/v1/auth/revoke
    revoke_res = await client.post(
        "/api/v1/auth/revoke",
        json={"token": access_token, "revoke_all_sessions": False},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert revoke_res.status_code == 200


@pytest.mark.asyncio
async def test_audit_logs_query(client: AsyncClient):
    res = await client.get("/api/v1/audit-logs?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_backups_api_workflow(client: AsyncClient):
    # 1. Create backup
    create_res = await client.post(
        "/api/v1/system/backups/create",
        json={"backup_type": "api_test", "notes": "API test backup"},
    )
    assert create_res.status_code == 201
    manifest = create_res.json()
    backup_id = manifest["backup_id"]

    # 2. List backups
    list_res = await client.get("/api/v1/system/backups")
    assert list_res.status_code == 200
    backups = list_res.json()["backups"]
    assert any(b["backup_id"] == backup_id for b in backups)

    # 3. Validate backup
    val_res = await client.post(f"/api/v1/system/backups/validate?backup_id={backup_id}")
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is True

    # 4. Dry-run restore
    restore_res = await client.post(
        "/api/v1/system/backups/restore",
        json={"backup_id": backup_id, "dry_run": True, "confirm": False},
    )
    assert restore_res.status_code == 200
    assert restore_res.json()["dry_run"] is True
