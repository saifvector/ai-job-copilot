"""
Unit tests for ATSEngine and Truthfulness Guardrail in Phase 7.
"""
from core.tailoring.ats_engine import ATSEngine
from schemas.tailoring import (
    ResumeSectionEducation,
    ResumeSectionExperience,
    ResumeSectionProject,
    ResumeSectionSkillGroup,
    ResumeVersionDTO,
)


def create_sample_version() -> ResumeVersionDTO:
    return ResumeVersionDTO(
        version_type="balanced",
        label="Version C: Balanced",
        summary="Senior Software Engineer with 6+ years of expertise in high-throughput backend APIs using Python and FastAPI.",
        skills=[
            ResumeSectionSkillGroup(
                category="Backend",
                skills=["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"],
            ),
            ResumeSectionSkillGroup(
                category="DevOps",
                skills=["Docker", "Git"],
            ),
        ],
        experience=[
            ResumeSectionExperience(
                company="TechCorp",
                role="Senior Backend Engineer",
                start_date="2022",
                end_date="Present",
                description="Engineered core microservices",
                bullet_points=[
                    "Architected high-throughput async APIs using FastAPI and PostgreSQL, reducing latency by 40%.",
                    "Scaled database connections and query indexes, supporting 50,000+ daily active users.",
                    "Automated integration testing pipelines using pytest and Docker containers.",
                ],
                highlighted_keywords=["FastAPI", "PostgreSQL", "Docker"],
            )
        ],
        education=[
            ResumeSectionEducation(
                institution="State University",
                degree="B.S. in Computer Science",
                field_of_study="Computer Science",
                start_date="2016",
                end_date="2020",
            )
        ],
        projects=[
            ResumeSectionProject(
                title="Distributed Job Runner",
                description="Asynchronous task dispatch engine",
                technologies=["Python", "FastAPI", "Redis"],
                bullet_points=["Engineered message queue consumer with 99.9% uptime."],
            )
        ],
    )


def test_calculate_ats_score_high_fit():
    version = create_sample_version()
    job_keywords = ["Python", "FastAPI", "PostgreSQL", "Docker"]
    required_skills = ["Python", "FastAPI"]
    preferred_skills = ["PostgreSQL", "Docker"]
    candidate_skills = ["Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "Docker", "Git"]

    breakdown = ATSEngine.calculate_ats_score(
        version=version,
        job_keywords=job_keywords,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        job_title="Senior Backend Engineer",
        job_description="Looking for a Senior Backend Engineer proficient in Python, FastAPI, and PostgreSQL to scale APIs.",
        candidate_genuine_skills=candidate_skills,
    )

    assert breakdown.overall_score >= 80.0
    assert breakdown.keyword_match >= 75.0
    assert breakdown.skill_match == 100.0
    assert breakdown.section_quality >= 75.0
    assert breakdown.formatting_structure >= 80.0
    assert len(breakdown.suggestions) >= 1


def test_calculate_ats_score_low_fit():
    version = create_sample_version()
    job_keywords = ["Ruby", "Rails", "Kubernetes", "AWS", "Elixir"]
    required_skills = ["Ruby", "Rails"]
    preferred_skills = ["Kubernetes", "AWS"]
    candidate_skills = ["Python", "FastAPI", "PostgreSQL"]

    breakdown = ATSEngine.calculate_ats_score(
        version=version,
        job_keywords=job_keywords,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        job_title="Lead Ruby on Rails Architect",
        job_description="Must have 10+ years of Ruby on Rails and Kubernetes experience.",
        candidate_genuine_skills=candidate_skills,
    )

    assert breakdown.overall_score < 75.0
    assert breakdown.skill_match < 50.0
    assert any("competencies currently absent" in s for s in breakdown.suggestions)


def test_enforce_truthfulness_strips_hallucinations():
    version = create_sample_version()
    # Add a fabricated skill group with skills candidate does not possess
    version.skills.append(
        ResumeSectionSkillGroup(
            category="Cloud & AI",
            skills=["Python", "Kubernetes", "Rust", "TensorFlow"],
        )
    )

    authentic_skills = ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL", "Docker", "Git"]

    sanitized_version, stripped = ATSEngine.enforce_truthfulness(
        version=version,
        authentic_skills=authentic_skills,
    )

    # Kubernetes, Rust, TensorFlow must be stripped
    assert "Kubernetes" in stripped
    assert "Rust" in stripped
    assert "TensorFlow" in stripped

    # All remaining skills must be authentic
    for group in sanitized_version.skills:
        for s in group.skills:
            assert s in authentic_skills or any(a.lower() in s.lower() for a in authentic_skills)
