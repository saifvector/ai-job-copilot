from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

ReportType = Literal[
    "APPLICATION_REPORT",
    "MATCH_REPORT",
    "SKILL_REPORT",
    "CAREER_REPORT",
    "RESUME_REPORT",
]

ExportFormat = Literal[
    "PDF",
    "CSV",
    "XLSX",
    "JSON",
]


class ReportGenerateRequest(BaseModel):
    """Payload to trigger report generation and export."""
    report_type: ReportType = Field(
        ...,
        description="Type of report to generate: APPLICATION_REPORT, MATCH_REPORT, SKILL_REPORT, CAREER_REPORT, RESUME_REPORT"
    )
    format: ExportFormat = Field(
        "PDF",
        description="Export format: PDF, CSV, XLSX, JSON"
    )
    title: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional custom report title"
    )
    date_range_days: Optional[int] = Field(
        30,
        ge=1,
        le=3650,
        description="Number of past days to include in analytics, or null for all time"
    )
    include_details: bool = Field(
        True,
        description="Whether to include granular item breakdowns in tables"
    )


class ReportResponse(BaseModel):
    """Report metadata and download reference."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID = Field(..., serialization_alias="userId")
    report_type: str = Field(..., serialization_alias="reportType")
    title: str
    format: str
    file_path: str = Field(..., serialization_alias="filePath")
    file_name: str = Field(..., serialization_alias="fileName")
    file_size: int = Field(..., serialization_alias="fileSize")
    download_count: int = Field(..., serialization_alias="downloadCount")
    generation_duration_ms: float = Field(..., serialization_alias="generationDurationMs")
    summary: Optional[str] = None
    generated_at: datetime = Field(..., serialization_alias="generatedAt")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    download_url: Optional[str] = Field(None, serialization_alias="downloadUrl")


class ReportListStats(BaseModel):
    """Aggregated report statistics for user dashboard."""
    model_config = ConfigDict(populate_by_name=True)

    total_reports: int = Field(0, serialization_alias="totalReports")
    total_downloads: int = Field(0, serialization_alias="totalDownloads")
    storage_used_bytes: int = Field(0, serialization_alias="storageUsedBytes")
    most_popular_type: Optional[str] = Field(None, serialization_alias="mostPopularType")


class ReportListResponse(BaseModel):
    """List of reports with aggregate metrics."""
    model_config = ConfigDict(populate_by_name=True)

    reports: List[ReportResponse]
    stats: ReportListStats
