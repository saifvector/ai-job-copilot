import json
import pytest
from core.exceptions import ValidationException
from schemas.resume_analysis import (
    ParsedResumeExtraction,
    RawParsedSkill,
    RawParsedProject,
    RawParsedEducation,
    RawParsedExperience,
    RawParsedCertification,
)
from services.resume_parser_service import ResumeParserService


def test_raw_parsed_skill_normalization():
    # Fuzzy category matches
    s1 = RawParsedSkill(name="Python", category="programming code language", confidence_score=0.98)
    assert s1.category == "Programming Language"
    assert s1.confidence_score == 0.98

    s2 = RawParsedSkill(name="React.js", category="Frontend Framework", confidence_score=1.0)
    assert s2.category == "Framework"

    s3 = RawParsedSkill(name="PostgreSQL", category="relational database", confidence_score=0.95)
    assert s3.category == "Database"

    s4 = RawParsedSkill(name="AWS ECS", category="cloud infrastructure", confidence_score=0.9)
    assert s4.category == "Cloud"

    s5 = RawParsedSkill(name="PyTorch", category="machine learning / ai", confidence_score=0.92)
    assert s5.category == "AI/ML"

    s6 = RawParsedSkill(name="Docker", category="devops tools", confidence_score=0.88)
    assert s6.category == "Tool"

    # Percentage confidence normalization (e.g. 95% -> 0.95)
    s7 = RawParsedSkill(name="Git", category="Tool", confidence_score=95)
    assert s7.confidence_score == 0.95


def test_raw_parsed_project_technologies_list():
    p1 = RawParsedProject(
        title="AI Job Copilot",
        description="Autonomous job hunting assistant",
        technologies=["Python", "FastAPI", "React"],
    )
    assert p1.technologies == ["Python", "FastAPI", "React"]

    # Comma-separated string converted to list
    p2 = RawParsedProject(
        title="Data Lakehouse",
        technologies="Spark, Kafka, BigQuery",
    )
    assert p2.technologies == ["Spark", "Kafka", "BigQuery"]


def test_parsed_resume_extraction_schema_valid():
    sample_data = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+1-555-0123",
        "summary": "AI & Data Science engineer with 5+ years building ML pipelines in Python and FastAPI.",
        "skills": [
            {"name": "Python", "category": "Programming Language", "confidence_score": 0.98},
            {"name": "FastAPI", "category": "Framework", "confidence_score": 0.95},
        ],
        "projects": [
            {
                "title": "ML Serving Platform",
                "description": "High-throughput model serving architecture.",
                "technologies": ["Python", "FastAPI", "Docker"],
            }
        ],
        "education": [
            {
                "institution": "Stanford University",
                "degree": "M.S.",
                "field_of_study": "Computer Science",
                "start_date": "2018",
                "end_date": "2020",
            }
        ],
        "experience": [
            {
                "company": "DeepMind Corp",
                "role": "Senior ML Engineer",
                "description": "Led production AI services serving 10M daily requests.",
                "start_date": "2020",
                "end_date": "Present",
            }
        ],
        "certifications": [
            {
                "name": "Google Cloud Professional ML Engineer",
                "issuer": "Google Cloud",
                "issue_date": "2022",
            }
        ],
    }

    parsed = ParsedResumeExtraction.model_validate(sample_data)
    assert parsed.name == "Jane Doe"
    assert parsed.email == "jane.doe@example.com"
    assert len(parsed.skills) == 2
    assert len(parsed.projects) == 1
    assert len(parsed.education) == 1
    assert len(parsed.experience) == 1
    assert len(parsed.certifications) == 1


def test_resume_parser_service_validate_invalid_json():
    class DummySession:
        pass

    service = ResumeParserService(session=DummySession(), orchestrator=None)

    with pytest.raises(ValidationException) as exc:
        service.validate_response("not valid json at all")
    assert "AI response is not valid JSON" in str(exc.value)
