"""
Unit tests for ReportService and Exporters (Phase 9 Reporting & Export Center).
Tests data collection, PDF generation, CSV generation, XLSX generation, and JSON generation.
"""
import os
import tempfile
import uuid
import openpyxl
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import UserModel
from models.job import JobModel
from models.application import ApplicationModel
from models.match_result import MatchResultModel
from repositories.report_repository import ReportRepository
from schemas.report import ReportGenerateRequest
from services.report_service import ReportService
from services.reporting.exporters.pdf_exporter import generate_pdf_report
from services.reporting.exporters.csv_exporter import generate_csv_report
from services.reporting.exporters.xlsx_exporter import generate_xlsx_report
from services.reporting.exporters.json_exporter import generate_json_report


@pytest.fixture
def temp_storage():
    """Create a temporary directory for report test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.mark.asyncio
async def test_generate_pdf_report(temp_storage):
    """Test ReportLab PDF exporter generates valid non-empty PDF file."""
    output_path = os.path.join(temp_storage, "test_app_report.pdf")
    sample_data = {
        "report_type": "APPLICATION_REPORT",
        "title": "Application Performance & Conversion Report",
        "user_name": "Alex Chen",
        "generated_at": "2026-09-27 12:00:00 UTC",
        "summary": {
            "total_applications": 12,
            "applications_sent": 10,
            "interviews_reached": 3,
            "offers_received": 1,
            "response_rate": 30.0,
            "interview_rate": 30.0,
            "offer_rate": 10.0,
        },
        "by_status": {
            "SAVED": 2,
            "APPLIED": 5,
            "INTERVIEW": 3,
            "OFFER": 1,
            "REJECTED": 1,
        },
        "applications": [
            {
                "company": "Linear",
                "job_title": "Lead Product Engineer",
                "status": "INTERVIEW",
                "source": "RemoteOK",
                "created_at": "2026-09-25",
                "interview_count": 2,
            },
            {
                "company": "Stripe",
                "job_title": "Staff Backend Engineer",
                "status": "APPLIED",
                "source": "Greenhouse",
                "created_at": "2026-09-26",
                "interview_count": 0,
            },
        ],
    }

    size = generate_pdf_report(sample_data, output_path)
    assert os.path.exists(output_path)
    assert size > 2000
    with open(output_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-"


@pytest.mark.asyncio
async def test_generate_csv_report(temp_storage):
    """Test CSV exporter generates RFC 4180 compliant CSV."""
    output_path = os.path.join(temp_storage, "test_report.csv")
    sample_data = {
        "report_type": "MATCH_REPORT",
        "title": "Job Match Compatibility Report",
        "user_name": "Alex Chen",
        "generated_at": "2026-09-27 12:00:00 UTC",
        "summary": {
            "total_matches_analyzed": 5,
            "average_match_score": 88.5,
        },
        "top_matches": [
            {
                "company": "Vercel",
                "job_title": "Full Stack Architect",
                "overall_score": 92.0,
                "match_level": "EXCELLENT",
                "skill_score": 95.0,
                "experience_score": 90.0,
                "recommendation": "Exceptional fit",
            }
        ],
    }

    size = generate_csv_report(sample_data, output_path)
    assert os.path.exists(output_path)
    assert size > 100

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Vercel" in content
        assert "Full Stack Architect" in content
        assert "92.0%" in content


@pytest.mark.asyncio
async def test_generate_xlsx_report(temp_storage):
    """Test openpyxl exporter generates multi-sheet workbook with Applications, Matches, Analytics."""
    output_path = os.path.join(temp_storage, "test_report.xlsx")
    sample_data = {
        "report_type": "APPLICATION_REPORT",
        "title": "Application Performance",
        "user_name": "Alex Chen",
        "generated_at": "2026-09-27",
        "summary": {
            "total_applications": 8,
            "applications_sent": 6,
            "interviews_reached": 2,
            "response_rate": 33.3,
            "interview_rate": 33.3,
            "offer_rate": 16.7,
        },
        "applications": [
            {
                "company": "GitHub",
                "job_title": "Senior Systems Engineer",
                "status": "APPLIED",
                "source": "Direct",
                "created_at": "2026-09-27",
                "interview_count": 1,
            }
        ],
    }
    context = {
        "applications": sample_data["applications"],
        "matches": [
            {
                "company": "GitHub",
                "job_title": "Senior Systems Engineer",
                "overall_score": 91.0,
                "match_level": "EXCELLENT",
                "skill_score": 90.0,
                "experience_score": 92.0,
                "matched_skills_count": 8,
                "missing_skills_count": 1,
                "recommendation": "High priority apply",
            }
        ],
        "summary": sample_data["summary"],
    }

    size = generate_xlsx_report(sample_data, context, output_path)
    assert os.path.exists(output_path)
    assert size > 2000

    wb = openpyxl.load_workbook(output_path)
    assert "Applications" in wb.sheetnames
    assert "Matches" in wb.sheetnames
    assert "Analytics" in wb.sheetnames

    ws_apps = wb["Applications"]
    assert ws_apps["A4"].value == "Company"
    assert ws_apps["A5"].value == "GitHub"


@pytest.mark.asyncio
async def test_generate_json_report(temp_storage):
    """Test JSON exporter creates valid structured JSON."""
    output_path = os.path.join(temp_storage, "test_report.json")
    sample_data = {
        "report_type": "SKILL_REPORT",
        "title": "Skill Gap Analysis",
        "summary": {"total_user_skills": 15},
    }
    size = generate_json_report(sample_data, output_path)
    assert os.path.exists(output_path)
    assert size > 50


@pytest.mark.asyncio
async def test_report_service_end_to_end(db_session: AsyncSession, temp_storage):
    """Test ReportService end-to-end generation and persistence."""
    user_id = uuid.UUID("a0000000-0000-0000-0000-000000000001")
    report_repo = ReportRepository(db_session)
    service = ReportService(report_repo=report_repo, session=db_session, storage_dir=temp_storage)

    # 1. Generate Application Report as PDF
    req_pdf = ReportGenerateRequest(
        report_type="APPLICATION_REPORT",
        format="PDF",
        title="My Q3 Application Performance",
        date_range_days=90,
    )
    report_pdf = await service.generateReport(user_id=user_id, request=req_pdf)

    assert report_pdf is not None
    assert report_pdf.report_type == "APPLICATION_REPORT"
    assert report_pdf.format == "PDF"
    assert report_pdf.file_size > 0
    assert report_pdf.download_count == 0
    assert report_pdf.generation_duration_ms > 0
    assert os.path.exists(report_pdf.file_path)

    # 2. Test Download tracking
    file_path, file_name, media_type = await service.downloadReport(report_pdf.id, user_id)
    assert file_path == report_pdf.file_path
    assert media_type == "application/pdf"

    # Reload from repo and verify download count was incremented
    reloaded = await report_repo.findById(report_pdf.id)
    assert reloaded.download_count == 1

    # 3. Generate Skill Report as XLSX
    req_xlsx = ReportGenerateRequest(
        report_type="SKILL_REPORT",
        format="XLSX",
    )
    report_xlsx = await service.generateReport(user_id=user_id, request=req_xlsx)
    assert report_xlsx.format == "XLSX"
    assert os.path.exists(report_xlsx.file_path)

    # 4. List reports
    reports, stats = await service.listReports(user_id=user_id)
    assert len(reports) >= 2
    assert stats["total_reports"] >= 2
    assert stats["total_downloads"] >= 1
    assert stats["storage_used_bytes"] > 0

    # 5. Delete report
    deleted = await service.deleteReport(report_pdf.id, user_id)
    assert deleted is True
    assert not os.path.exists(report_pdf.file_path)
