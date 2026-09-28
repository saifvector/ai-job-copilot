"""
Integration tests for Phase 6 Dashboard and Analytics REST API endpoints:
- GET /api/v1/dashboard
- GET /api/v1/dashboard/profile-health
- GET /api/v1/dashboard/readiness
- GET /api/v1/dashboard/skills
- GET /api/v1/dashboard/analytics
- POST /api/v1/dashboard/snapshot
"""
import uuid
import pytest
from httpx import AsyncClient
import models
from sqlalchemy import select
from tests.conftest import DEMO_USER_ID, TestSessionFactory


@pytest.fixture(autouse=True)
async def seed_dashboard_test_data():
    """Seed test profile, skills, jobs, and matches into SQLite test DB."""
    async with TestSessionFactory() as session:
        # 1. Seed or update profile for DEMO_USER_ID
        stmt = select(models.ProfileModel).where(models.ProfileModel.user_id == DEMO_USER_ID)
        profile_res = await session.execute(stmt)
        existing_profile = profile_res.scalars().first()
        if not existing_profile:
            profile = models.ProfileModel(
                user_id=DEMO_USER_ID,
                summary="Senior Full-Stack & Cloud Architect with 6 years experience.",
                preferred_roles=["Senior Software Engineer", "Backend Architect"],
                preferred_locations=["Remote", "New York"],
                years_of_experience=6,
            )
            session.add(profile)
        else:
            existing_profile.summary = "Senior Full-Stack & Cloud Architect with 6 years experience."
            existing_profile.preferred_roles = ["Senior Software Engineer", "Backend Architect"]
            existing_profile.preferred_locations = ["Remote", "New York"]
            existing_profile.years_of_experience = 6
            session.add(existing_profile)

        # 2. Seed Skills
        s1 = models.SkillModel(user_id=DEMO_USER_ID, name="Python", category="Language", confidence_score=0.95)
        s2 = models.SkillModel(user_id=DEMO_USER_ID, name="FastAPI", category="Framework", confidence_score=0.9)
        s3 = models.SkillModel(user_id=DEMO_USER_ID, name="PostgreSQL", category="Database", confidence_score=0.88)
        s4 = models.SkillModel(user_id=DEMO_USER_ID, name="Docker", category="Cloud", confidence_score=0.85)
        session.add_all([s1, s2, s3, s4])

        # 3. Seed Job and MatchResult
        job_id = uuid.UUID("d0000000-0000-0000-0000-000000000001")
        existing_job = await session.get(models.JobModel, job_id)
        if not existing_job:
            job = models.JobModel(
                id=job_id,
                source="RemoteOK",
                external_id="dashboard-test-job-1",
                title="Lead Backend Engineer",
                company="Nexus AI",
                location="Remote",
                employment_type="Full-time",
                salary_min=175000,
                salary_max=220000,
                currency="USD",
                description="Lead our distributed backend Python infrastructure.",
                requirements="5+ years Python, Docker, Kubernetes.",
                apply_url="https://example.com/jobs/nexus-1",
            )
            session.add(job)
            await session.flush()

            js1 = models.JobSkillModel(job_id=job_id, skill_name="Python")
            js2 = models.JobSkillModel(job_id=job_id, skill_name="Kubernetes")
            session.add_all([js1, js2])

        # Seed MatchResult
        match_stmt = select(models.MatchResultModel).where(
            models.MatchResultModel.user_id == DEMO_USER_ID,
            models.MatchResultModel.job_id == job_id,
        )
        existing_match = (await session.execute(match_stmt)).scalars().first()
        if not existing_match:
            match = models.MatchResultModel(
                user_id=DEMO_USER_ID,
                job_id=job_id,
                overall_score=88.5,
                skill_score=85.0,
                experience_score=90.0,
                education_score=80.0,
                location_score=100.0,
                role_score=90.0,
                strengths=["Python proficiency", "Remote compatibility"],
                missing_skills=["Kubernetes"],
                recommendations=["Learn Kubernetes cluster orchestration."],
            )
            session.add(match)

        await session.commit()


@pytest.mark.asyncio
async def test_get_dashboard_overview(client: AsyncClient):
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "totalJobs" in data
    assert "jobsMatched" in data
    assert "averageMatchScore" in data
    assert "excellentMatches" in data
    assert "topMatches" in data
    assert len(data["topMatches"]) >= 1
    assert data["topMatches"][0]["company"] == "Nexus AI"
    assert data["profileScore"] > 0
    assert data["readinessScore"] > 0


@pytest.mark.asyncio
async def test_get_profile_health(client: AsyncClient):
    response = await client.get("/api/v1/dashboard/profile-health")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert 0.0 <= data["overallScore"] <= 100.0
    assert "breakdown" in data
    assert "resumeCompleteness" in data["breakdown"]
    assert "skillCoverage" in data["breakdown"]
    assert "experienceCoverage" in data["breakdown"]
    assert "educationCoverage" in data["breakdown"]
    assert isinstance(data["actionableRecommendations"], list)


@pytest.mark.asyncio
async def test_get_career_readiness(client: AsyncClient):
    response = await client.get("/api/v1/dashboard/readiness")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert 0.0 <= data["careerReadinessScore"] <= 100.0
    assert data["tier"] in ["Market Leader", "Market Ready", "Advancing Competency", "Developing Profile"]
    assert "factors" in data
    assert len(data["explanation"]) > 10


@pytest.mark.asyncio
async def test_get_skill_gap_analysis(client: AsyncClient):
    response = await client.get("/api/v1/dashboard/skills")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "mostRequestedSkills" in data
    assert "missingSkills" in data
    assert "recommendations" in data


@pytest.mark.asyncio
async def test_get_analytics_dashboard(client: AsyncClient):
    response = await client.get("/api/v1/dashboard/analytics")
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "matchDistribution" in data
    assert "items" in data["matchDistribution"]
    assert "topSkills" in data
    assert "missingSkills" in data
    assert "locationDistribution" in data
    assert "profileProgress" in data
    assert data["latencyMs"] >= 0


@pytest.mark.asyncio
async def test_create_analytics_snapshot(client: AsyncClient):
    response = await client.post("/api/v1/dashboard/snapshot")
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    data = res["data"]
    assert "id" in data
    assert data["profileScore"] > 0
    assert data["readinessScore"] > 0
