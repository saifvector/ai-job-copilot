import docx
import io
import json
import pytest
from fastapi import Depends
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession
from core.ai.base import AIProvider
from core.ai.orchestrator import AIOrchestrator
from core.dependencies import get_db, get_resume_parser_service
from main import app
from services.resume_parser_service import ResumeParserService


class MockTestProvider(AIProvider):
    @property
    def model_name(self) -> str:
        return "gemini-2.5-pro"

    async def generate_json(self, prompt: str, system_instruction: str = None) -> str:
        return json.dumps({
            "name": "Alex Chen",
            "email": "alex.chen@example.com",
            "phone": "+1 (555) 019-2834",
            "summary": "AI & Data Science student with experience in Python, Machine Learning, FastAPI and Deep Learning projects.",
            "skills": [
                {"name": "Python", "category": "Programming Language", "confidence_score": 0.98},
                {"name": "FastAPI", "category": "Framework", "confidence_score": 0.95},
                {"name": "PostgreSQL", "category": "Database", "confidence_score": 0.90},
                {"name": "AWS", "category": "Cloud", "confidence_score": 0.85},
            ],
            "projects": [
                {
                    "title": "AI Job Copilot",
                    "description": "Autonomous full-stack agent with Gemini intelligence.",
                    "technologies": ["Python", "FastAPI", "Next.js"],
                }
            ],
            "education": [
                {
                    "institution": "University of Technology",
                    "degree": "B.S. in Computer Science",
                    "field_of_study": "Software Engineering",
                    "start_date": "2020",
                    "end_date": "2024",
                }
            ],
            "experience": [
                {
                    "company": "TechNova Corp",
                    "role": "AI Engineer Intern",
                    "description": "Engineered distributed LLM data processing pipelines.",
                    "start_date": "2023",
                    "end_date": "2024",
                }
            ],
            "certifications": [
                {
                    "name": "Google Professional Cloud Architect",
                    "issuer": "Google",
                    "issue_date": "2024",
                }
            ],
        })


def create_sample_docx_bytes() -> bytes:
    doc = docx.Document()
    doc.add_paragraph("Alex Chen - Staff Software Engineer")
    doc.add_paragraph("Summary: AI & Data Science engineer with experience in Python and FastAPI.")
    doc.add_paragraph("Skills: Python, FastAPI, PostgreSQL, AWS")
    doc.add_paragraph("Projects: AI Job Copilot using Python and Next.js")
    doc.add_paragraph("Education: B.S. in Computer Science at University of Technology")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_parse_resume_without_upload_returns_404(client: AsyncClient):
    # User has not uploaded any resume yet
    response = await client.post("/api/v1/resume/parse")
    assert response.status_code == 404
    body = response.json()
    assert "No resume found" in body["error"]["message"]


@pytest.mark.asyncio
async def test_full_resume_parse_and_intelligence_endpoints(
    client: AsyncClient,
    temp_storage,
):
    provider, _ = temp_storage
    # 1. Override the ResumeParserService to use MockTestProvider
    mock_orchestrator = AIOrchestrator(
        pro_provider=MockTestProvider(),
        flash_provider=MockTestProvider(),
    )

    def override_parser_service(
        session: AsyncSession = Depends(get_db),
    ):
        return ResumeParserService(
            session=session,
            orchestrator=mock_orchestrator,
            storage_provider=provider,
        )

    app.dependency_overrides[get_resume_parser_service] = override_parser_service




    try:
        # 2. Upload a valid docx resume first
        docx_bytes = create_sample_docx_bytes()
        files = {
            "file": (
                "alex_chen_resume.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }
        upload_resp = await client.post("/api/v1/resume/upload", files=files)
        assert upload_resp.status_code == 201

        # 3. Trigger Resume Parse endpoint: POST /api/v1/resume/parse
        parse_resp = await client.post("/api/v1/resume/parse")
        assert parse_resp.status_code == 200
        parse_data = parse_resp.json()["data"]

        assert parse_data["candidate"]["name"] == "Alex Chen"
        assert parse_data["candidate"]["phone"] == "+1 (555) 019-2834"
        assert "AI & Data Science student" in parse_data["summary"]
        assert len(parse_data["skills"]) == 4
        assert len(parse_data["projects"]) == 1
        assert len(parse_data["education"]) == 1
        assert len(parse_data["experience"]) == 1
        assert len(parse_data["certifications"]) == 1
        assert parse_data["modelUsed"] == "gemini-2.5-pro"

        # 4. GET /api/v1/profile/summary
        summary_resp = await client.get("/api/v1/profile/summary")
        assert summary_resp.status_code == 200
        summary_data = summary_resp.json()["data"]
        assert "AI & Data Science student" in summary_data["summary"]

        # 5. GET /api/v1/profile/skills
        skills_resp = await client.get("/api/v1/profile/skills")
        assert skills_resp.status_code == 200
        all_skills = skills_resp.json()["data"]
        assert len(all_skills) == 4

        # Filter by category
        filtered_resp = await client.get("/api/v1/profile/skills?category=Programming%20Language")
        assert filtered_resp.status_code == 200
        filtered_skills = filtered_resp.json()["data"]
        assert len(filtered_skills) == 1
        assert filtered_skills[0]["name"] == "Python"
        assert filtered_skills[0]["category"] == "Programming Language"

        # 6. GET /api/v1/profile/projects
        projects_resp = await client.get("/api/v1/profile/projects")
        assert projects_resp.status_code == 200
        projects_data = projects_resp.json()["data"]
        assert len(projects_data) == 1
        assert projects_data[0]["title"] == "AI Job Copilot"

        # 7. GET /api/v1/profile/full
        full_resp = await client.get("/api/v1/profile/full")
        assert full_resp.status_code == 200
        full_data = full_resp.json()["data"]
        assert full_data["candidate"]["name"] == "Alex Chen"
        assert len(full_data["education"]) == 1
        assert len(full_data["experience"]) == 1
        assert len(full_data["certifications"]) == 1

    finally:
        app.dependency_overrides.pop(get_resume_parser_service, None)
