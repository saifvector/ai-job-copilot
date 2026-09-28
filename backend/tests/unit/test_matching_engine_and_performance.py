"""
Unit tests for MatchingEngine orchestration, recommendation generator, and bulk performance (< 2s for 500 jobs).
"""
import time
import uuid
import pytest
from core.matching.base import CandidateProfileDTO, JobProfileDTO, ScoringWeights
from core.matching.engine import MatchingEngine
from core.matching.experience_matcher import ExperienceMatchResult
from core.matching.recommendation_generator import RecommendationGenerator
from core.matching.role_matcher import RoleMatchResult
from core.matching.skill_matcher import SkillMatchResult


@pytest.fixture
def candidate_dto():
    return CandidateProfileDTO(
        user_id=uuid.uuid4(),
        preferred_roles=["AI Engineer", "Backend Developer"],
        preferred_locations=["Remote"],
        years_of_experience=5,
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Machine Learning"],
        educations=[{"degree": "Bachelor of Technology", "field_of_study": "Computer Science"}],
        experiences=[{"role": "Backend Engineer", "company": "Tech Corp"}],
    )


@pytest.mark.asyncio
async def test_matching_engine_weights_and_composite_score(candidate_dto):
    weights = ScoringWeights(
        skill_weight=0.50,
        experience_weight=0.20,
        role_weight=0.15,
        location_weight=0.10,
        education_weight=0.05,
    )
    engine = MatchingEngine(weights=weights)

    job = JobProfileDTO(
        id=uuid.uuid4(),
        title="Senior AI Engineer",
        company="Global AI",
        location="Remote",
        skills=["Python", "FastAPI", "Docker", "Kubernetes"],
    )

    result = await engine.score_job(candidate=candidate_dto, job=job, generate_ai=False)

    assert 0.0 <= result.overall_score <= 100.0
    assert result.overall_score >= 75.0  # High alignment
    assert "Python" in result.matched_skills
    assert "Kubernetes" in result.missing_skills
    assert len(result.strengths) > 0
    assert len(result.recommendations) > 0


@pytest.mark.asyncio
async def test_recommendation_generator_fallback(candidate_dto):
    gen = RecommendationGenerator(ai_provider=None)
    job = JobProfileDTO(
        id=uuid.uuid4(),
        title="Cloud Software Engineer",
        company="Cloud Scale",
        location="Remote",
        skills=["Python", "AWS", "Terraform"],
    )

    skill_res = SkillMatchResult(
        score=50.0,
        matched_skills=["Python"],
        missing_skills=["AWS", "Terraform"],
    )
    exp_res = ExperienceMatchResult(
        score=90.0,
        candidate_years=5,
        required_years=3,
        seniority_aligned=True,
    )
    role_res = RoleMatchResult(score=80.0, matched_role="Backend Developer")

    analysis = gen.generate_fallback(
        candidate=candidate_dto,
        job=job,
        skill_result=skill_res,
        experience_result=exp_res,
        role_result=role_res,
        overall_score=75.0,
    )

    assert any("Python" in s for s in analysis.strengths)
    assert "AWS" in analysis.missing_skills
    assert "Terraform" in analysis.missing_skills
    # Recommendations should contain learning guidance for missing skills
    assert any("AWS" in r or "Cloud" in r for r in analysis.recommendations)


@pytest.mark.asyncio
async def test_bulk_matching_performance_500_jobs(candidate_dto):
    """
    Performance Requirement:
    Target: < 2 seconds for matching 500 jobs.
    """
    engine = MatchingEngine()

    # Generate 500 synthetic job postings
    mock_jobs = []
    technologies = ["Python", "FastAPI", "Docker", "AWS", "Kubernetes", "PostgreSQL", "React", "TypeScript", "Go"]
    locations = ["Remote", "San Francisco, CA", "New York, NY", "London, UK", "Bengaluru, India"]

    for i in range(500):
        mock_jobs.append(
            JobProfileDTO(
                id=uuid.uuid4(),
                title=f"Engineer Role {i % 10}",
                company=f"Company {i}",
                location=locations[i % len(locations)],
                skills=[technologies[i % len(technologies)], technologies[(i + 1) % len(technologies)]],
                description="Software engineering position building scalable distributed systems with 3+ years experience.",
            )
        )

    start_time = time.perf_counter()
    results = await engine.match_jobs_batch(candidate=candidate_dto, jobs=mock_jobs, top_n_ai=0)
    duration = time.perf_counter() - start_time

    assert len(results) == 500
    # Must be sorted descending by overall match score
    assert results[0].overall_score >= results[-1].overall_score
    # Critical SLA: must execute in under 2.0 seconds
    assert duration < 2.0, f"500-job matching took {duration:.3f}s, exceeding 2.0s SLA requirement!"
