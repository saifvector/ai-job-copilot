import uuid
import pytest
from httpx import AsyncClient
from core.security.api_keys import ApiKeyService
from models.job import JobModel
from models.user import UserModel


@pytest.mark.asyncio
async def test_public_api_auth_requirements(client: AsyncClient):
    # 1. Access without key returns 401
    res = await client.get("/api/public/v1/profile")
    assert res.status_code == 401
    assert "API_KEY_MISSING" in res.text or "UNAUTHORIZED" in res.text

    # 2. Access with invalid key returns 401
    res_invalid = await client.get(
        "/api/public/v1/profile",
        headers={"X-API-Key": "ajc_live_invalid_key_string_here"},
    )
    assert res_invalid.status_code == 401


@pytest.mark.asyncio
async def test_public_api_endpoints_end_to_end(client: AsyncClient, db_session):
    # Create test user
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Public API Tester",
        email=f"public_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)

    # Create target job
    job = JobModel(
        external_id=f"ext_{uuid.uuid4().hex[:8]}",
        title="Staff Platform Engineer",
        company="Stripe",
        location="Remote",
        employment_type="Full-time",
        description="Build developer platforms and public APIs.",
        apply_url="https://stripe.com/jobs/123",
        source="remoteok",
    )
    db_session.add(job)
    await db_session.flush()

    # Generate API key with required scopes
    key_service = ApiKeyService(db_session)
    _, raw_key = await key_service.create_api_key(
        user_id=user_id,
        name="Automated Public Test Key",
        scopes=[
            "read:profile",
            "read:resume",
            "read:matches",
            "read:applications",
            "write:applications",
            "read:reports",
        ],
    )
    await db_session.commit()

    headers = {"X-API-Key": raw_key}

    # 1. GET /api/public/v1/profile
    prof_res = await client.get("/api/public/v1/profile", headers=headers)
    assert prof_res.status_code == 200
    prof_data = prof_res.json()
    assert prof_data["name"] == "Public API Tester"

    # 2. GET /api/public/v1/resumes
    res_res = await client.get("/api/public/v1/resumes", headers=headers)
    assert res_res.status_code == 200
    assert "items" in res_res.json()

    # 3. GET /api/public/v1/matches
    match_res = await client.get("/api/public/v1/matches", headers=headers)
    assert match_res.status_code == 200
    assert "items" in match_res.json()

    # 4. POST /api/public/v1/applications
    app_payload = {
        "job_id": str(job.id),
        "status": "Applied",
        "notes": "Submitted via Third-party Public API Client",
    }
    create_res = await client.post("/api/public/v1/applications", json=app_payload, headers=headers)
    assert create_res.status_code == 201
    created_app = create_res.json()
    assert created_app["job_id"] == str(job.id)
    assert created_app["status"] == "Applied"
    app_id = created_app["id"]

    # 5. GET /api/public/v1/applications
    list_app_res = await client.get("/api/public/v1/applications", headers=headers)
    assert list_app_res.status_code == 200
    assert list_app_res.json()["total"] >= 1

    # 6. GET /api/public/v1/applications/{id}
    get_app_res = await client.get(f"/api/public/v1/applications/{app_id}", headers=headers)
    assert get_app_res.status_code == 200
    assert get_app_res.json()["id"] == app_id

    # 7. GET /api/public/v1/reports
    rep_res = await client.get("/api/public/v1/reports", headers=headers)
    assert rep_res.status_code == 200
    assert "items" in rep_res.json()
