import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from models.application import ApplicationModel
from models.job import JobModel
from models.user import UserModel


@pytest.mark.asyncio
async def test_career_intelligence_api_endpoints(client: AsyncClient, db_session):
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Career Intelligence Candidate",
        email=f"intel_api_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)

    job_id = uuid.uuid4()
    job = JobModel(
        id=job_id,
        source="Company Site",
        external_id="api-job-1",
        title="Senior Machine Learning Engineer",
        company="OpenAI",
        location="San Francisco, CA",
        description="Build state-of-the-art models",
        apply_url="https://openai.com/careers",
    )
    db_session.add(job)

    app_id = uuid.uuid4()
    app = ApplicationModel(
        id=app_id,
        user_id=user_id,
        job_id=job_id,
        status="APPLIED",
        application_date=datetime.now(timezone.utc),
        source="Company Site",
    )
    db_session.add(app)
    await db_session.commit()

    headers = {"X-User-Id": str(user_id)}

    # 1. Record an Outcome Event via POST /api/v1/intelligence/outcomes
    record_res = await client.post(
        "/api/v1/intelligence/outcomes",
        json={
            "application_id": str(app_id),
            "outcome_type": "InterviewReceived",
            "notes": "First round with Engineering Manager",
            "metadata": {"round": 1, "interviewer": "Engineering Lead"},
        },
        headers=headers,
    )
    assert record_res.status_code == 201
    evt_data = record_res.json()
    assert evt_data["outcome_type"] == "InterviewReceived"
    assert evt_data["application_id"] == str(app_id)
    assert evt_data["job_title"] == "Senior Machine Learning Engineer"
    assert evt_data["company"] == "OpenAI"

    # 2. List Outcomes via GET /api/v1/intelligence/outcomes
    list_res = await client.get("/api/v1/intelligence/outcomes", headers=headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert list_data["items"][0]["outcome_type"] == "InterviewReceived"

    # 3. Get Analytics via GET /api/v1/intelligence/analytics
    analytics_res = await client.get("/api/v1/intelligence/analytics", headers=headers)
    assert analytics_res.status_code == 200
    an_data = analytics_res.json()
    assert an_data["total_applications"] >= 1
    assert an_data["interviews_received"] >= 1
    assert an_data["interview_rate"] >= 0.5

    # 4. Get Skills via GET /api/v1/intelligence/skills
    skills_res = await client.get("/api/v1/intelligence/skills", headers=headers)
    assert skills_res.status_code == 200
    skills_data = skills_res.json()
    assert "items" in skills_data
    assert "disclaimer" in skills_data

    # 5. Get Resumes via GET /api/v1/intelligence/resumes
    resumes_res = await client.get("/api/v1/intelligence/resumes", headers=headers)
    assert resumes_res.status_code == 200
    res_data = resumes_res.json()
    assert "items" in res_data

    # 6. Get Companies via GET /api/v1/intelligence/companies
    comp_res = await client.get("/api/v1/intelligence/companies", headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    assert comp_data["total_companies"] >= 1
    assert comp_data["companies"][0]["company"] == "OpenAI"

    # 7. Get Strategy via GET /api/v1/intelligence/strategy
    strat_res = await client.get("/api/v1/intelligence/strategy", headers=headers)
    assert strat_res.status_code == 200
    strat_data = strat_res.json()
    assert "source_breakdown" in strat_data
    assert "key_insights" in strat_data

    # 8. Get Recommendations via GET /api/v1/intelligence/recommendations
    recs_res = await client.get("/api/v1/intelligence/recommendations", headers=headers)
    assert recs_res.status_code == 200
    recs_data = recs_res.json()
    assert len(recs_data["recommendations"]) >= 1

    # 9. Get Trends via GET /api/v1/intelligence/trends
    trends_res = await client.get("/api/v1/intelligence/trends?days=60", headers=headers)
    assert trends_res.status_code == 200
    trends_data = trends_res.json()
    assert "trends" in trends_data
    assert "cohorts" in trends_data

    # 10. Capture Snapshot via POST /api/v1/intelligence/snapshots
    snap_res = await client.post("/api/v1/intelligence/snapshots", headers=headers)
    assert snap_res.status_code == 201
    snap_data = snap_res.json()
    assert snap_data["total_applications"] >= 1

    # 11. Complete Overview via GET /api/v1/intelligence/overview
    overview_res = await client.get("/api/v1/intelligence/overview", headers=headers)
    assert overview_res.status_code == 200
    overview_data = overview_res.json()
    assert overview_data["analytics"]["total_applications"] >= 1
    assert "recommendations" in overview_data
