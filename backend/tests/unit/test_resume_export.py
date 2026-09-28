"""
Unit tests for ResumeExportService (PDF, DOCX, Markdown) in Phase 7.
"""
from core.tailoring.export_service import ResumeExportService
from schemas.tailoring import (
    ResumeSectionEducation,
    ResumeSectionExperience,
    ResumeSectionProject,
    ResumeSectionSkillGroup,
    ResumeVersionDTO,
)


def get_test_version() -> ResumeVersionDTO:
    return ResumeVersionDTO(
        version_type="ats",
        label="Version A: ATS Optimized",
        summary="Experienced Software Engineer specialized in async backend architectures and distributed data pipelines.",
        skills=[
            ResumeSectionSkillGroup(
                category="Programming Languages",
                skills=["Python", "TypeScript", "SQL"],
            ),
            ResumeSectionSkillGroup(
                category="Frameworks & Tools",
                skills=["FastAPI", "Next.js", "Docker", "PostgreSQL"],
            ),
        ],
        experience=[
            ResumeSectionExperience(
                company="Nexus Systems",
                role="Senior Software Engineer",
                start_date="2021",
                end_date="Present",
                description="Designed high-scale web platforms",
                bullet_points=[
                    "Spearheaded redesign of transactional database queries, reducing p99 latency by 45%.",
                    "Developed asynchronous worker pipelines handling 2.5M events daily with 99.95% reliability.",
                ],
                highlighted_keywords=["FastAPI", "PostgreSQL"],
            )
        ],
        education=[
            ResumeSectionEducation(
                institution="Massachusetts Institute of Technology",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2017",
                end_date="2021",
            )
        ],
        projects=[
            ResumeSectionProject(
                title="Cloud Monitor",
                description="Real-time latency dashboard",
                technologies=["FastAPI", "React", "Docker"],
                bullet_points=["Engineered WebSocket metrics streamer."],
            )
        ],
    )


def test_export_markdown():
    version = get_test_version()
    contact = {"email": "alex@example.com", "phone": "+1-555-0199", "location": "San Francisco, CA"}
    md = ResumeExportService.export_markdown(
        version=version,
        candidate_name="Alex Chen",
        contact_info=contact,
    )

    assert "# Alex Chen" in md
    assert "alex@example.com" in md
    assert "## PROFESSIONAL SUMMARY" in md
    assert "## CORE COMPETENCIES & TECHNICAL SKILLS" in md
    assert "**Programming Languages**: Python, TypeScript, SQL" in md
    assert "## PROFESSIONAL EXPERIENCE" in md
    assert "Nexus Systems" in md
    assert "Spearheaded redesign" in md
    assert "## EDUCATION & CREDENTIALS" in md


def test_export_docx():
    version = get_test_version()
    contact = {"email": "alex@example.com", "phone": "+1-555-0199"}
    docx_bytes = ResumeExportService.export_docx(
        version=version,
        candidate_name="Alex Chen",
        contact_info=contact,
    )

    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 2000
    # Check standard DOCX / ZIP magic bytes PK\x03\x04
    assert docx_bytes[:4] == b"PK\x03\x04"


def test_export_pdf():
    version = get_test_version()
    contact = {"email": "alex@example.com", "phone": "+1-555-0199", "location": "Austin, TX"}
    pdf_bytes = ResumeExportService.export_pdf(
        version=version,
        candidate_name="Alex Chen",
        contact_info=contact,
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # Check PDF magic bytes %PDF-
    assert pdf_bytes[:5] == b"%PDF-"
