"""
ReportService for Phase 9 Reporting & Export Center.
Coordinates report data gathering, multi-format export engines (PDF, CSV, XLSX, JSON),
observability metrics, and file downloads.
"""
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import get_logger
from models.report import ReportModel
from repositories.report_repository import ReportRepository
from schemas.report import ExportFormat, ReportGenerateRequest, ReportType
from services.reporting.data_collectors import (
    collect_application_report_data,
    collect_career_report_data,
    collect_match_report_data,
    collect_resume_report_data,
    collect_skill_report_data,
)
from services.reporting.exporters.csv_exporter import generate_csv_report
from services.reporting.exporters.json_exporter import generate_json_report
from services.reporting.exporters.pdf_exporter import generate_pdf_report
from services.reporting.exporters.xlsx_exporter import generate_xlsx_report

logger = get_logger(__name__)

MEDIA_TYPE_MAP: Dict[str, str] = {
    "PDF": "application/pdf",
    "CSV": "text/csv; charset=utf-8",
    "XLSX": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "JSON": "application/json; charset=utf-8",
}


class ReportService:
    """
    Service layer orchestrating the Reporting & Export Center.
    """

    def __init__(
        self,
        report_repo: ReportRepository,
        session: AsyncSession,
        storage_dir: Optional[str] = None,
    ) -> None:
        self.report_repo = report_repo
        self.session = session
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.storage_dir = os.path.join(base_dir, "storage", "reports")
        os.makedirs(self.storage_dir, exist_ok=True)

    # 1. Report Data Generation Handlers
    async def generateApplicationReport(
        self,
        user_id: uuid.UUID,
        days: Optional[int] = 30,
    ) -> Dict[str, Any]:
        """Generate structured dataset for Application Performance Report."""
        return await collect_application_report_data(user_id, self.session, days)

    async def generateMatchReport(
        self,
        user_id: uuid.UUID,
        days: Optional[int] = 30,
    ) -> Dict[str, Any]:
        """Generate structured dataset for Job Match Score Report."""
        return await collect_match_report_data(user_id, self.session, days)

    async def generateSkillReport(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Generate structured dataset for Skill Gap & Roadmap Report."""
        return await collect_skill_report_data(user_id, self.session)

    async def generateCareerReport(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Generate structured dataset for Career Readiness Report."""
        return await collect_career_report_data(user_id, self.session)

    async def generateResumeReport(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Generate structured dataset for Resume Performance Report."""
        return await collect_resume_report_data(user_id, self.session)

    # 2. Exporters
    def exportPDF(self, data: Dict[str, Any], output_path: str) -> int:
        """Export report dataset as styled PDF."""
        return generate_pdf_report(data, output_path)

    def exportCSV(self, data: Dict[str, Any], output_path: str) -> int:
        """Export report dataset as CSV."""
        return generate_csv_report(data, output_path)

    def exportXLSX(self, data: Dict[str, Any], output_path: str, context: Optional[Dict[str, Any]] = None) -> int:
        """Export report dataset as multi-sheet XLSX."""
        return generate_xlsx_report(data, context or {}, output_path)

    def exportJSON(self, data: Dict[str, Any], output_path: str) -> int:
        """Export report dataset as formatted JSON."""
        return generate_json_report(data, output_path)

    # 3. Main Workflow Orchestrator
    async def generateReport(
        self,
        user_id: uuid.UUID,
        request: ReportGenerateRequest,
    ) -> ReportModel:
        """
        End-to-end report generation pipeline:
        1. Collect dataset based on report_type
        2. Format output file using requested exporter
        3. Record generation duration and file metadata
        4. Persist to database and return ReportModel
        """
        start_time = time.perf_counter()
        report_type = request.report_type.upper()
        export_format = request.format.upper()
        days = request.date_range_days

        logger.info(f"Generating {report_type} in {export_format} format for user {user_id}...")

        # 1. Collect Report Data
        if report_type == "APPLICATION_REPORT":
            data = await self.generateApplicationReport(user_id, days)
        elif report_type == "MATCH_REPORT":
            data = await self.generateMatchReport(user_id, days)
        elif report_type == "SKILL_REPORT":
            data = await self.generateSkillReport(user_id)
        elif report_type == "CAREER_REPORT":
            data = await self.generateCareerReport(user_id)
        elif report_type == "RESUME_REPORT":
            data = await self.generateResumeReport(user_id)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

        # Set title if specified
        if request.title:
            data["title"] = request.title

        title = data.get("title", f"{report_type.replace('_', ' ').title()}")

        # 2. Determine file paths
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        slug_title = "".join(c if c.isalnum() else "_" for c in title.lower())[:30]
        file_ext = export_format.lower()
        file_name = f"{slug_title}_{timestamp_str}.{file_ext}"
        output_path = os.path.join(self.storage_dir, file_name)

        # 3. Invoke Export Engine
        if export_format == "PDF":
            file_size = self.exportPDF(data, output_path)
        elif export_format == "CSV":
            file_size = self.exportCSV(data, output_path)
        elif export_format == "XLSX":
            # For XLSX, gather supplementary context across all dimensions
            app_data = data if report_type == "APPLICATION_REPORT" else await self.generateApplicationReport(user_id, 90)
            match_data = data if report_type == "MATCH_REPORT" else await self.generateMatchReport(user_id, 90)
            context = {
                "applications": app_data.get("applications", []),
                "matches": match_data.get("top_matches", []),
                "summary": app_data.get("summary", {}),
            }
            file_size = self.exportXLSX(data, output_path, context)
        elif export_format == "JSON":
            file_size = self.exportJSON(data, output_path)
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Summary text for preview
        summary_text = (
            f"{title} containing {len(data.get('applications', data.get('top_matches', data.get('priorities', []))))} records. "
            f"Generated in {duration_ms}ms."
        )

        # 4. Save to Repository
        report = await self.report_repo.create({
            "id": uuid.uuid4(),
            "user_id": user_id,
            "report_type": report_type,
            "title": title,
            "format": export_format,
            "file_path": output_path,
            "file_name": file_name,
            "file_size": file_size,
            "download_count": 0,
            "generation_duration_ms": duration_ms,
            "summary": summary_text,
            "generated_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
        })

        logger.info(
            f"Report {report.id} ({file_name}, {file_size} bytes) created in {duration_ms}ms"
        )
        return report

    async def listReports(
        self,
        user_id: uuid.UUID,
        report_type: Optional[str] = None,
        export_format: Optional[str] = None,
    ) -> Tuple[List[ReportModel], Dict[str, Any]]:
        """List all reports and retrieve aggregate usage statistics."""
        reports = await self.report_repo.findByUser(user_id, report_type, export_format)
        stats = await self.report_repo.getStats(user_id)
        return reports, stats

    async def getReportById(
        self,
        report_id: Union[uuid.UUID, str],
        user_id: uuid.UUID,
    ) -> Optional[ReportModel]:
        """Get report by ID for a user."""
        report = await self.report_repo.findById(report_id)
        if report and report.user_id == user_id:
            return report
        return None

    async def downloadReport(
        self,
        report_id: Union[uuid.UUID, str],
        user_id: uuid.UUID,
    ) -> Tuple[str, str, str]:
        """
        Record download metric and return (file_path, file_name, media_type).
        Raises FileNotFoundError if file is missing.
        """
        report = await self.getReportById(report_id, user_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        if not os.path.exists(report.file_path):
            raise FileNotFoundError(f"Report file {report.file_path} is missing from disk")

        # Increment download counter
        await self.report_repo.incrementDownloadCount(report.id)

        media_type = MEDIA_TYPE_MAP.get(report.format.upper(), "application/octet-stream")
        return report.file_path, report.file_name, media_type

    async def deleteReport(
        self,
        report_id: Union[uuid.UUID, str],
        user_id: uuid.UUID,
    ) -> bool:
        """Delete report record and remove file from disk."""
        report = await self.getReportById(report_id, user_id)
        if not report:
            return False

        # Attempt to delete file from disk
        try:
            if os.path.exists(report.file_path):
                os.remove(report.file_path)
        except Exception as exc:
            logger.warning(f"Could not remove report file {report.file_path}: {exc}")

        return await self.report_repo.delete(report.id)
