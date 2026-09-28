"""
Integration tests for Application Tracking System REST API (Phase 8).
Validates endpoints under /api/v1/applications.
"""
import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from models.job import JobModel
from models.user import UserModel


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_application_lifecycle_api(client: AsyncClient, db_session, mock_user_id):
    """Test full application lifecycle through REST endpoints."""
    # 1. Create a test job in db
    job = JobModel(
        id=uuid.uuid4(),
        source="Greenhouse",
        external_id=f"gh-api-{uuid.uuid4().hex[:8]}",
        title="Staff Infrastructure Architect",
        company="Snowflake Partner",
        location="Remote, US",
        description="Lead distributed cloud architecture.",
        apply_url="https://example.com/apply/snowflake",
    )
    db_session.add(job)
    await db_session.commit()

    # 2. POST /api/v1/applications - Track as SAVED
    payload = {
        "job_id": str(job.id),
        "status": "SAVED",
        "source": "Greenhouse",
        "notes": "Target company for Q4",
    }
    response = await client.post(
        "/api/v1/applications",
        json=payload,
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    app_id = data["data"]["id"]
    assert data["data"]["status"] == "SAVED"
    assert data["data"]["job"]["company"] == "Snowflake Partner"

    # 3. GET /api/v1/applications - List
    list_res = await client.get(
        "/api/v1/applications",
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["success"] is True
    assert any(a["id"] == app_id for a in list_data["data"])

    # 4. GET /api/v1/applications/pipeline - Kanban
    pipeline_res = await client.get(
        "/api/v1/applications/pipeline",
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert pipeline_res.status_code == 200
    pipeline_data = pipeline_res.json()["data"]
    assert any(a["id"] == app_id for a in pipeline_data["saved"])

    # 5. PATCH /api/v1/applications/{id}/status - Transition to APPLIED
    status_res = await client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "APPLIED", "notes": "Submitted official application"},
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert status_res.status_code == 200
    assert status_res.json()["data"]["status"] == "APPLIED"

    # 6. POST /api/v1/applications/{id}/events - Add custom event
    event_res = await client.post(
        f"/api/v1/applications/{app_id}/events",
        json={
            "event_type": "RECRUITER_CONTACT",
            "description": "Recruiter reached out via email to schedule call.",
        },
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert event_res.status_code == 201
    assert event_res.json()["data"]["event_type"] == "RECRUITER_CONTACT"

    # 7. POST /api/v1/applications/{id}/interviews - Schedule interview
    interview_res = await client.post(
        f"/api/v1/applications/{app_id}/interviews",
        json={
            "interview_type": "HR",
            "interview_date": "2026-10-10T15:00:00Z",
            "interview_round": 1,
            "notes": "Introductory phone screen",
        },
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert interview_res.status_code == 201
    assert interview_res.json()["data"]["interview_type"] == "HR"

    # 8. GET /api/v1/applications/{id} - Full details
    detail_res = await client.get(
        f"/api/v1/applications/{app_id}",
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert detail_res.status_code == 200
    detail_data = detail_res.json()["data"]
    assert detail_data["status"] == "INTERVIEW"
    assert len(detail_data["interviews"]) == 1
    assert len(detail_data["events"]) >= 3

    # 9. GET /api/v1/applications/analytics
    analytics_res = await client.get(
        "/api/v1/applications/analytics",
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()["data"]
    assert analytics_data["total_applications"] >= 1
    assert analytics_data["applications_sent"] >= 1
    assert analytics_data["interview_rate"] >= 0.0

    # 10. DELETE /api/v1/applications/{id}
    del_res = await client.delete(
        f"/api/v1/applications/{app_id}",
        headers={"X-User-Id": str(mock_user_id)},
    )
    assert del_res.status_code == 200
    assert del_res.json()["data"] is True
