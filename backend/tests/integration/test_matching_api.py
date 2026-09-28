"""
Integration tests for Phase 5 AI Job Matching REST API endpoints:
- POST /api/v1/matching/run
- GET /api/v1/matching/results
- GET /api/v1/matching/results/{jobId}
- GET /api/v1/matching/top
"""
import uuid
import pytest
from httpx import AsyncClient
import models
from sqlalchemy import select
from tests.conftest import DEMO_USER_ID, TestSessionFactory


@pytest.fixture(autouse=True)
async def seed_matching_test_data():
    """Seed test profile and test jobs into SQLite test DB."""
    async with TestSessionFactory() as session:
        # 1. Seed or update profile for DEMO_USER_ID
        stmt = select(models.ProfileModel).where(models.ProfileModel.user_id == DEMO_USER_ID)
        profile_res = await session.execute(stmt)
        existing_profile = profile_res.scalars().first()
        if not existing_profile:
            profile = models.ProfileModel(
                user_id=DEMO_USER_ID,
                summary="Senior Fullstack & AI Engineer with extensive Python experience.",
                preferred_roles=["AI Engineer", "Backend Developer"],
                preferred_locations=["Remote", "San Francisco"],
                years_of_experience=4,
            )
            session.add(profile)
        else:
            existing_profile.preferred_roles = ["AI Engineer", "Backend Developer"]
            existing_profile.preferred_locations = ["Remote", "San Francisco"]
            existing_profile.years_of_experience = 4
            session.add(existing_profile)

        # 2. Seed Skills
        skill1 = models.SkillModel(
            user_id=DEMO_USER_ID,
            name="Python",
            category="Programming Language",
            confidence_score=0.95,
        )
        skill2 = models.SkillModel(
            user_id=DEMO_USER_ID,
            name="FastAPI",
            category="Framework",
            confidence_score=0.90,
        )
        skill3 = models.SkillModel(
            user_id=DEMO_USER_ID,
            name="PostgreSQL",
            category="Database",
            confidence_score=0.88,
        )
        session.add_all([skill1, skill2, skill3])

        # 3. Seed test Job
        test_job_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")
        existing_job = await session.get(models.JobModel, test_job_id)
        if not existing_job:
            job = models.JobModel(
                id=test_job_id,
                source="RemoteOK",
                external_id="matching-test-job-1",
                title="Senior AI Backend Engineer",
                company="OpenAI Partner",
                location="Remote",
                employment_type="Full-time",
                salary_min=160000,
                salary_max=210000,
                currency="USD",
                description="Looking for an AI engineer with strong Python, FastAPI, and Docker skills.",
                requirements="3+ years of experience with Python and microservices.",
                apply_url="https://example.com/apply/1",
            )
            session.add(job)
            await session.flush()

            js1 = models.JobSkillModel(job_id=test_job_id, skill_name="Python")
            js2 = models.JobSkillModel(job_id=test_job_id, skill_name="FastAPI")
            js3 = models.JobSkillModel(job_id=test_job_id, skill_name="Docker")
            session.add_all([js1, js2, js3])

        await session.commit()


@pytest.mark.asyncio
async def test_run_matching_endpoint(client: AsyncClient):
    response = await client.post("/api/v1/matching/run", json={"limit": 50})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["matchesSaved"] >= 1
    assert data["data"]["durationMs"] > 0
    assert 0.0 <= data["data"]["topScore"] <= 100.0


@pytest.mark.asyncio
async def test_get_matching_results_endpoint(client: AsyncClient):
    # First ensure matching has run
    await client.post("/api/v1/matching/run")

    response = await client.get("/api/v1/matching/results?page=1&pageSize=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "pagination" in data["data"]
    items = data["data"]["items"]
    assert len(items) >= 1

    first_match = items[0]
    assert "overallScore" in first_match
    assert "skillScore" in first_match
    assert "experienceScore" in first_match
    assert "roleScore" in first_match
    assert "strengths" in first_match
    assert "missingSkills" in first_match
    assert "recommendations" in first_match
    assert first_match["job"] is not None
    assert "title" in first_match["job"]


@pytest.mark.asyncio
async def test_get_matching_results_filtered_by_score(client: AsyncClient):
    await client.post("/api/v1/matching/run")

    # Filter with high min score
    response = await client.get("/api/v1/matching/results?minScore=50.0")
    assert response.status_code == 200
    data = response.json()
    for item in data["data"]["items"]:
        assert item["overallScore"] >= 50.0


@pytest.mark.asyncio
async def test_get_top_matches_endpoint(client: AsyncClient):
    await client.post("/api/v1/matching/run")

    response = await client.get("/api/v1/matching/top?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1
    # Check sorted descending
    scores = [item["overallScore"] for item in data["data"]]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_get_match_result_by_job_id(client: AsyncClient):
    test_job_id = "c0000000-0000-0000-0000-000000000001"
    response = await client.get(f"/api/v1/matching/results/{test_job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["jobId"] == test_job_id
    assert "overallScore" in data["data"]
    assert "strengths" in data["data"]
    assert "recommendations" in data["data"]
