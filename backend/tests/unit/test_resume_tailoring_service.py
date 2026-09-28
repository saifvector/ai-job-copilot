"""
Unit tests for ResumeTailoringService in Phase 7.
"""
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from core.ai.orchestrator import AIOrchestrator
from schemas.tailoring import ResumeVersionDTO
from services.resume_tailoring_service import ResumeTailoringService


def make_skill(name: str, cat: str):
    m = MagicMock()
    m.name = name
    m.category = cat
    return m


def make_exp(company: str, role: str, desc: str):
    m = MagicMock()
    m.id = uuid.uuid4()
    m.company = company
    m.role = role
    m.start_date = "2022"
    m.end_date = "Present"
    m.description = desc
    return m


def make_edu(inst: str, deg: str):
    m = MagicMock()
    m.id = uuid.uuid4()
    m.institution = inst
    m.degree = deg
    m.field_of_study = "Computer Science"
    m.start_date = "2018"
    m.end_date = "2022"
    return m


@pytest.fixture
def mock_tailoring_service():
    tailored_repo = AsyncMock()
    job_repo = AsyncMock()
    user_repo = AsyncMock()
    profile_repo = AsyncMock()
    resume_repo = AsyncMock()
    skill_repo = AsyncMock()
    experience_repo = AsyncMock()
    education_repo = AsyncMock()
    project_repo = AsyncMock()
    certification_repo = AsyncMock()
    orchestrator = AsyncMock(spec=AIOrchestrator)

    service = ResumeTailoringService(
        tailored_repo=tailored_repo,
        job_repo=job_repo,
        user_repo=user_repo,
        profile_repo=profile_repo,
        resume_repo=resume_repo,
        skill_repo=skill_repo,
        experience_repo=experience_repo,
        education_repo=education_repo,
        project_repo=project_repo,
        certification_repo=certification_repo,
        orchestrator=orchestrator,
    )
    return service


@pytest.mark.asyncio
async def test_analyze_job_description_fallback(mock_tailoring_service):
    # Simulate AI exception to verify deterministic fallback
    mock_tailoring_service.orchestrator.execute_with_fallback.side_effect = Exception("AI offline")

    kw = await mock_tailoring_service.analyze_job_description(
        job_description="We need a Python and FastAPI engineer with PostgreSQL and Docker experience to build high-scale APIs.",
        job_title="Senior Backend Engineer",
        job_company="Acme Cloud",
    )

    assert len(kw.keywords) >= 2
    assert "Python" in kw.keywords or "FastAPI" in kw.keywords
    assert kw.coverage_percentage == 0.0


@pytest.mark.asyncio
async def test_generate_tailored_resume_pipeline(mock_tailoring_service):
    user_id = uuid.uuid4()
    job_id = uuid.uuid4()

    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.name = "Jordan Lee"
    mock_user.email = "jordan@example.com"
    mock_tailoring_service.user_repo.get_by_id.return_value = mock_user

    mock_job = MagicMock()
    mock_job.id = job_id
    mock_job.title = "Lead Backend Engineer"
    mock_job.company = "Stripe"
    mock_job.description = "Seeking a Lead Backend Engineer with expertise in Python, FastAPI, PostgreSQL, and Docker."
    mock_job.requirements = "5+ years backend engineering."
    mock_tailoring_service.job_repo.get_by_id.return_value = mock_job

    mock_profile = MagicMock()
    mock_profile.summary = "Experienced full stack developer."
    mock_tailoring_service.profile_repo.get_by_user_id.return_value = mock_profile

    mock_tailoring_service.resume_repo.find_by_user.return_value = None
    mock_tailoring_service.skill_repo.get_by_user_id.return_value = [
        make_skill("Python", "Programming Language"),
        make_skill("FastAPI", "Framework"),
        make_skill("PostgreSQL", "Database"),
        make_skill("Docker", "DevOps"),
    ]
    mock_tailoring_service.experience_repo.get_by_user_id.return_value = [
        make_exp("Acme Corp", "Backend Engineer", "Built scalable APIs in FastAPI and managed PostgreSQL databases.")
    ]
    mock_tailoring_service.education_repo.get_by_user_id.return_value = [
        make_edu("Stanford University", "B.S.")
    ]
    mock_tailoring_service.project_repo.get_by_user_id.return_value = []
    mock_tailoring_service.certification_repo.get_by_user_id.return_value = []

    # Mock AI orchestrator to trigger deterministic generator
    mock_tailoring_service.orchestrator.execute_with_fallback.side_effect = Exception("AI offline")

    # Mock DB storage
    mock_saved = MagicMock()
    mock_saved.id = uuid.uuid4()
    mock_saved.user_id = user_id
    mock_saved.job_id = job_id
    mock_saved.original_resume_id = None
    mock_saved.title = "Lead Backend Engineer — Tailored Resume"
    mock_saved.summary = "High-impact software engineer..."
    mock_saved.ats_score = 88.5
    mock_saved.keyword_coverage = 85.0
    mock_saved.created_at = "2026-09-27T20:00:00Z"
    mock_saved.updated_at = "2026-09-27T20:00:00Z"

    mock_tailoring_service.tailored_repo.findByJob.return_value = None
    mock_tailoring_service.tailored_repo.create.return_value = mock_saved

    res = await mock_tailoring_service.generate_tailored_resume(
        user_id=user_id,
        job_id=job_id,
        target_version="balanced",
    )

    assert res.job_id == job_id
    assert res.user_id == user_id
    assert "ats" in res.versions
    assert "recruiter" in res.versions
    assert "balanced" in res.versions
    assert res.ats_score > 0
    assert res.keyword_coverage > 0
    assert len(res.recommendations) > 0


@pytest.mark.asyncio
async def test_export_resume(mock_tailoring_service):
    user_id = uuid.uuid4()
    tailored_id = uuid.uuid4()

    mock_response = MagicMock()
    mock_response.title = "Senior_Developer"
    sample_v = ResumeVersionDTO(
        version_type="balanced",
        label="Version C",
        summary="Summary test",
        skills=[],
        experience=[],
        education=[],
        projects=[],
        certifications=[],
    )
    mock_response.versions = {"balanced": sample_v}
    mock_tailoring_service.get_tailored_resume_by_id = AsyncMock(return_value=mock_response)

    mock_user = MagicMock()
    mock_user.name = "Test User"
    mock_user.email = "test@example.com"
    mock_user.phone = "12345"
    mock_tailoring_service.user_repo.get_by_id.return_value = mock_user

    # Test PDF
    content, media_type, filename = await mock_tailoring_service.export_resume(
        user_id=user_id,
        tailored_id=tailored_id,
        format_type="pdf",
        version_type="balanced",
    )
    assert media_type == "application/pdf"
    assert filename.endswith(".pdf")
    assert content.startswith(b"%PDF-")

    # Test Markdown
    content_md, media_type_md, filename_md = await mock_tailoring_service.export_resume(
        user_id=user_id,
        tailored_id=tailored_id,
        format_type="markdown",
        version_type="balanced",
    )
    assert "text/markdown" in media_type_md
    assert filename_md.endswith(".md")
    assert "# Test User" in content_md.decode("utf-8")
