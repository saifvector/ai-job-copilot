"""
Unit tests for AnalyticsService:
- calculateProfileHealth
- calculateCareerReadiness
- generateSkillGapAnalysis
- generateAnalyticsSnapshot
- getAnalytics chart compiler
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.analytics_service import AnalyticsService


@pytest.fixture
def mock_repos():
    analytics_repo = AsyncMock()
    user_repo = AsyncMock()
    profile_repo = AsyncMock()
    resume_repo = AsyncMock()
    skill_repo = AsyncMock()
    experience_repo = AsyncMock()
    education_repo = AsyncMock()

    return {
        "analytics_repo": analytics_repo,
        "user_repo": user_repo,
        "profile_repo": profile_repo,
        "resume_repo": resume_repo,
        "skill_repo": skill_repo,
        "experience_repo": experience_repo,
        "education_repo": education_repo,
    }


@pytest.fixture
def analytics_service(mock_repos):
    return AnalyticsService(
        analytics_repo=mock_repos["analytics_repo"],
        user_repo=mock_repos["user_repo"],
        profile_repo=mock_repos["profile_repo"],
        resume_repo=mock_repos["resume_repo"],
        skill_repo=mock_repos["skill_repo"],
        experience_repo=mock_repos["experience_repo"],
        education_repo=mock_repos["education_repo"],
    )


@pytest.mark.asyncio
async def test_calculate_profile_health_empty_profile(analytics_service, mock_repos):
    user_id = uuid.uuid4()
    mock_repos["profile_repo"].get_by_user_id.return_value = None
    mock_repos["resume_repo"].find_by_user.return_value = None
    mock_repos["skill_repo"].get_by_user_id.return_value = []
    mock_repos["experience_repo"].get_by_user_id.return_value = []
    mock_repos["education_repo"].get_by_user_id.return_value = []

    health = await analytics_service.calculateProfileHealth(user_id)

    assert health.overall_score < 30.0
    assert health.breakdown.resume_completeness == 0.0
    assert health.breakdown.skill_coverage == 15.0
    assert len(health.actionable_recommendations) > 0


@pytest.mark.asyncio
async def test_calculate_profile_health_complete_profile(analytics_service, mock_repos):
    user_id = uuid.uuid4()

    mock_profile = MagicMock()
    mock_profile.summary = "Senior Full-Stack Architect with extensive experience in cloud microservices."
    mock_profile.preferred_roles = ["Senior Engineer", "Architect"]
    mock_profile.years_of_experience = 8
    mock_repos["profile_repo"].get_by_user_id.return_value = mock_profile

    mock_resume = MagicMock()
    mock_resume.original_filename = "resume.pdf"
    mock_repos["resume_repo"].find_by_user.return_value = mock_resume

    mock_skills = [
        MagicMock(name=f"Skill{i}", category=f"Cat{i % 4}", confidence_score=0.9)
        for i in range(12)
    ]
    mock_repos["skill_repo"].get_by_user_id.return_value = mock_skills

    mock_experiences = [
        MagicMock(company=f"Company{i}", role="Lead Dev", description="Built scalable microservices")
        for i in range(3)
    ]
    mock_repos["experience_repo"].get_by_user_id.return_value = mock_experiences

    mock_educations = [
        MagicMock(degree="Bachelor of Science", field_of_study="Computer Science", institution="MIT")
    ]
    mock_repos["education_repo"].get_by_user_id.return_value = mock_educations

    health = await analytics_service.calculateProfileHealth(user_id)

    assert health.overall_score == 100.0
    assert health.breakdown.resume_completeness == 100.0
    assert health.breakdown.skill_coverage == 100.0
    assert health.breakdown.experience_coverage == 100.0
    assert health.breakdown.education_coverage == 100.0
    assert len(health.strengths) >= 3


@pytest.mark.asyncio
async def test_calculate_career_readiness_market_ready(analytics_service, mock_repos):
    user_id = uuid.uuid4()

    # Health returns 85%
    mock_repos["profile_repo"].get_by_user_id.return_value = MagicMock(
        summary="Experienced Python and React full-stack builder.",
        preferred_roles=["Fullstack"],
        years_of_experience=5,
    )
    mock_repos["resume_repo"].find_by_user.return_value = MagicMock(original_filename="cv.pdf")
    def make_skill(name, cat, conf):
        s = MagicMock()
        s.name = name
        s.category = cat
        s.confidence_score = conf
        return s

    mock_repos["skill_repo"].get_by_user_id.return_value = [
        make_skill("Python", "Language", 0.95),
        make_skill("FastAPI", "Framework", 0.9),
        make_skill("React", "Frontend", 0.88),
        make_skill("PostgreSQL", "Database", 0.85),
    ]
    mock_repos["experience_repo"].get_by_user_id.return_value = [
        MagicMock(company="Tech Co", role="Developer", description="Fullstack apps"),
        MagicMock(company="Cloud Co", role="Engineer", description="Backend APIs"),
    ]
    mock_repos["education_repo"].get_by_user_id.return_value = [
        MagicMock(degree="B.S.", field_of_study="Software Engineering", institution="Stanford")
    ]

    mock_repos["analytics_repo"].get_match_distribution.return_value = {
        "excellent": 15,
        "strong": 20,
        "moderate": 10,
        "weak": 5,
        "total": 50,
        "avg_score": 76.5,
    }

    readiness = await analytics_service.calculateCareerReadiness(user_id)

    assert readiness.career_readiness_score >= 70.0
    assert readiness.tier in ["Market Ready", "Market Leader"]
    assert len(readiness.key_competencies) > 0
    assert len(readiness.growth_priorities) > 0


@pytest.mark.asyncio
async def test_generate_skill_gap_analysis(analytics_service, mock_repos):
    user_id = uuid.uuid4()

    mock_match1 = MagicMock()
    mock_match1.missing_skills = ["AWS", "Docker"]
    mock_match1.job = MagicMock(
        skills=[
            MagicMock(skill_name="Python"),
            MagicMock(skill_name="AWS"),
            MagicMock(skill_name="Docker"),
        ]
    )

    mock_match2 = MagicMock()
    mock_match2.missing_skills = ["AWS", "Kubernetes"]
    mock_match2.job = MagicMock(
        skills=[
            MagicMock(skill_name="Python"),
            MagicMock(skill_name="AWS"),
            MagicMock(skill_name="Kubernetes"),
        ]
    )

    mock_repos["analytics_repo"].get_all_matches_with_jobs.return_value = [mock_match1, mock_match2]
    mock_repos["skill_repo"].get_by_user_id.return_value = [
        MagicMock(name="Python", category="Language", confidence_score=0.95),
    ]

    gap_analysis = await analytics_service.generateSkillGapAnalysis(user_id)

    assert gap_analysis.total_analyzed_jobs == 2
    assert gap_analysis.candidate_skills_count == 1

    # AWS should be in missing skills
    missing_names = [m.name for m in gap_analysis.missing_skills]
    assert "AWS" in missing_names
    assert len(gap_analysis.recommendations) > 0
