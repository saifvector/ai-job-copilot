"""
Integration tests for Application Assistant REST API (Phase 12).
Validates endpoints under:
- POST  /api/v1/application-assistant/create
- GET   /api/v1/application-assistant/analytics
- GET   /api/v1/application-assistant/drafts
- GET   /api/v1/application-assistant/{id}
- POST  /api/v1/application-assistant/generate-answers
- PATCH /api/v1/application-assistant/review
- GET   /api/v1/application-assistant/{id}/checklist
- POST  /api/v1/application-assistant/{id}/submit
- DELETE /api/v1/application-assistant/{id}
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.job import JobModel
from tests.conftest import TestSessionFactory


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.fixture
async def target_job() -> JobModel:
    async with TestSessionFactory() as session:
        job = JobModel(
            source="Direct",
            external_id=f"job-{uuid.uuid4().hex[:8]}",
            title="Lead Cloud Architect",
            company="Apex Cloud Dynamics",
            location="Remote",
            description="Seeking an architect with deep knowledge in distributed cloud systems, Python, and microservices.",
            salary_min=160000.0,
            salary_max=190000.0,
            currency="USD",
            apply_url="https://example.com/jobs/apply/2",
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job


@pytest.mark.asyncio
async def test_application_assistant_api_full_flow(
    client: AsyncClient,
    mock_user_id: uuid.UUID,
    target_job: JobModel,
):
    """Test full Application Assistant API lifecycle: create, generate, review, checklist, submit."""
    headers = {"X-User-Id": str(mock_user_id)}

    # 1. Create Draft
    create_payload = {
        "jobId": str(target_job.id),
        "notes": "Target application with priority referral.",
    }
    create_res = await client.post("/api/v1/application-assistant/create", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    draft_data = create_res.json()["data"]
    draft_id = draft_data["id"]
    assert draft_data["jobId"] == str(target_job.id)
    assert draft_data["status"] == "Draft"
    assert len(draft_data["questions"]) >= 6

    # 2. Get Draft by ID
    get_res = await client.get(f"/api/v1/application-assistant/{draft_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == draft_id

    # 3. Generate Answers
    gen_payload = {
        "draftId": draft_id,
        "regenerateAll": True,
    }
    gen_res = await client.post("/api/v1/application-assistant/generate-answers", json=gen_payload, headers=headers)
    assert gen_res.status_code == 200
    gen_data = gen_res.json()["data"]
    first_q = gen_data["questions"][0]
    assert first_q["generatedAnswer"] is not None
    assert len(first_q["generatedAnswer"]) > 0

    # 4. Review Answers (User edits answer and confirms accuracy)
    review_payload = {
        "draftId": draft_id,
        "answers": [
            {
                "questionId": first_q["id"],
                "userAnswer": "Apex Cloud Dynamics has pioneered distributed cloud computing, which directly aligns with my 5+ years of engineering leadership.",
                "isReviewed": True,
            }
        ],
        "confirmAccuracy": True,
    }
    review_res = await client.patch("/api/v1/application-assistant/review", json=review_payload, headers=headers)
    assert review_res.status_code == 200
    reviewed_data = review_res.json()["data"]
    assert reviewed_data["status"] in ("ReadyForReview", "Draft")

    # 5. Evaluate Checklist
    checklist_res = await client.get(f"/api/v1/application-assistant/{draft_id}/checklist", headers=headers)
    assert checklist_res.status_code == 200
    checklist_data = checklist_res.json()["data"]
    assert "readinessScore" in checklist_data
    assert len(checklist_data["items"]) >= 3

    # 6. Candidate Explicit Submission Confirmation
    submit_res = await client.post(f"/api/v1/application-assistant/{draft_id}/submit", headers=headers)
    assert submit_res.status_code == 200
    submitted_data = submit_res.json()["data"]
    assert submitted_data["status"] == "SubmittedByUser"
    assert submitted_data["submittedAt"] is not None

    # 7. List Drafts
    list_res = await client.get("/api/v1/application-assistant/drafts", headers=headers)
    assert list_res.status_code == 200
    drafts = list_res.json()["data"]
    assert any(d["id"] == draft_id for d in drafts)

    # 8. Analytics
    analytics_res = await client.get("/api/v1/application-assistant/analytics", headers=headers)
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()["data"]
    assert analytics_data["draftsCreated"] >= 1
    assert analytics_data["draftsCompleted"] >= 1

    # 9. Delete Draft
    del_res = await client.delete(f"/api/v1/application-assistant/{draft_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["data"] is True
