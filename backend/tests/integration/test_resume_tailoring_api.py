"""
Integration tests for Phase 7 AI Resume Tailoring REST API endpoints:
- POST /api/v1/resume/tailor
- GET /api/v1/resume/tailored
- GET /api/v1/resume/tailored/{id}
- GET /api/v1/resume/tailored/{id}/export
"""
import uuid
import pytest
from httpx import AsyncClient
import models
from sqlalchemy import select
from tests.conftest import DEMO_USER_ID, TestSessionFactory

TAILOR_TEST_JOB_ID = uuid.UUID("e0000000-0000-0000-0000-000000000001")


@pytest.fixture(autouse=True)
async def seed_tailoring_test_data():
    """Seed test profile, skills, experience, and target job into SQLite test DB."""
    async with TestSessionFactory() as session:
        # Seed Profile
        stmt = select(models.ProfileModel).where(models.ProfileModel.user_id == DEMO_USER_ID)
        res = await session.execute(stmt)
        existing_profile = res.scalars().first()
        if not existing_profile:
            profile = models.ProfileModel(
                user_id=DEMO_USER_ID,
                summary="Senior Full-Stack Engineer with 7 years of distributed systems experience.",
                preferred_roles=["Senior Backend Engineer", "Lead Developer"],
                preferred_locations=["Remote"],
                years_of_experience=7,
            )
            session.add(profile)

        # Seed Skills
        skills = [
            models.SkillModel(user_id=DEMO_USER_ID, name="Python", category="Language", confidence_score=1.0),
            models.SkillModel(user_id=DEMO_USER_ID, name="FastAPI", category="Framework", confidence_score=1.0),
            models.SkillModel(user_id=DEMO_USER_ID, name="PostgreSQL", category="Database", confidence_score=1.0),
            models.SkillModel(user_id=DEMO_USER_ID, name="Docker", category="DevOps", confidence_score=0.9),
            models.SkillModel(user_id=DEMO_USER_ID, name="TypeScript", category="Language", confidence_score=0.85),
        ]
        session.add_all(skills)

        # Seed Experience
        exp = models.ExperienceModel(
            user_id=DEMO_USER_ID,
            company="CloudScale Inc",
            role="Senior Systems Architect",
            start_date="2021",
            end_date="Present",
            description="Architected high-throughput async microservices using FastAPI, Python, and PostgreSQL.",
        )
        session.add(exp)

        # Seed Target Job
        existing_job = await session.get(models.JobModel, TAILOR_TEST_JOB_ID)
        if not existing_job:
            job = models.JobModel(
                id=TAILOR_TEST_JOB_ID,
                source="RemoteOK",
                external_id="tailor-test-job-1",
                title="Principal Backend Engineer",
                company="Acme Cloud",
                location="Remote",
                employment_type="Full-time",
                salary_min=180000,
                salary_max=230000,
                currency="USD",
                description="We are seeking a Principal Backend Engineer proficient in Python, FastAPI, and PostgreSQL to scale microservices and APIs.",
                requirements="7+ years building async distributed web services with Python and relational databases.",
                apply_url="https://example.com/apply/principal-backend",
            )
            session.add(job)

        await session.commit()


@pytest.mark.asyncio
async def test_tailor_resume_and_list_flow(client: AsyncClient):
    # 1. Trigger Resume Tailoring
    tailor_payload = {
        "jobId": str(TAILOR_TEST_JOB_ID),
        "targetVersion": "balanced",
        "customInstructions": "Highlight performance optimizations and query latency reductions.",
    }
    response = await client.post("/api/v1/resume/tailor", json=tailor_payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["success"] is True

    tailored_resume = data["data"]
    tailored_id = tailored_resume["id"]
    assert tailored_resume["jobId"] == str(TAILOR_TEST_JOB_ID)
    assert tailored_resume["atsScore"] > 0
    assert tailored_resume["keywordCoverage"] > 0
    assert "ats" in tailored_resume["versions"]
    assert "recruiter" in tailored_resume["versions"]
    assert "balanced" in tailored_resume["versions"]

    # 2. List Tailored Resumes
    list_res = await client.get("/api/v1/resume/tailored")
    assert list_res.status_code == 200
    list_data = list_res.json()["data"]
    assert len(list_data) >= 1
    assert any(item["id"] == tailored_id for item in list_data)

    # 3. Get Tailored Resume by ID
    get_res = await client.get(f"/api/v1/resume/tailored/{tailored_id}")
    assert get_res.status_code == 200
    single_data = get_res.json()["data"]
    assert single_data["id"] == tailored_id
    assert single_data["atsBreakdown"]["overallScore"] > 0
    assert len(single_data["recommendations"]) > 0

    # 4. Export as PDF
    pdf_res = await client.get(f"/api/v1/resume/tailored/{tailored_id}/export?format=pdf&version=ats")
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers["content-type"]
    assert pdf_res.content.startswith(b"%PDF-")
    assert "attachment; filename=" in pdf_res.headers["content-disposition"]

    # 5. Export as DOCX
    docx_res = await client.get(f"/api/v1/resume/tailored/{tailored_id}/export?format=docx&version=recruiter")
    assert docx_res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in docx_res.headers["content-type"]
    assert docx_res.content[:4] == b"PK\x03\x04"

    # 6. Export as Markdown
    md_res = await client.get(f"/api/v1/resume/tailored/{tailored_id}/export?format=markdown&version=balanced")
    assert md_res.status_code == 200
    assert "text/markdown" in md_res.headers["content-type"]
    md_text = md_res.content.decode("utf-8")
    assert "# " in md_text
    assert "## PROFESSIONAL SUMMARY" in md_text
