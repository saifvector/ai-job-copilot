import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from core.dependencies import (
    get_ai_cost_service,
    get_authenticated_user_id,
    get_backup_service,
    get_monitoring_service,
    get_task_queue,
)
from core.security.file_security import FileSecurityValidator
from schemas.ai_cost import AICostSummaryResponse
from schemas.backup import (
    BackupCreateRequest,
    BackupListResponse,
    BackupMetadataResponse,
    BackupRestoreRequest,
    BackupRestoreResponse,
    BackupValidationResponse,
)
from schemas.monitoring import MonitoringMetricsResponse
from schemas.security import FileValidationResult
from services.ai_cost_service import AICostService
from services.backup_service import BackupService
from services.monitoring_service import MonitoringService
from workers.task_queue import BackgroundTaskQueue

router = APIRouter(prefix="/system", tags=["System Operations & Observability"])


@router.get(
    "/metrics",
    response_model=MonitoringMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Production Metrics Dashboard",
    description="Returns detailed latency percentiles (p50, p95, p99), error rates by category, AI usage, and database diagnostics.",
)
async def get_metrics_dashboard(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
) -> MonitoringMetricsResponse:
    metrics = await monitoring_service.get_dashboard_metrics()
    return MonitoringMetricsResponse.model_validate(metrics)


@router.get(
    "/ai-costs",
    response_model=AICostSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI Usage & Cost Accounting",
    description="Tracks tokens consumed, requests made, model-by-model pricing, and user budget quotas.",
)
async def get_ai_costs(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter AI costs by user UUID"),
    timeframe: str = Query("all", description="Billing timeframe: all, 30d, 7d"),
    ai_service: AICostService = Depends(get_ai_cost_service),
) -> AICostSummaryResponse:
    summary = ai_service.get_summary(user_id=user_id, timeframe=timeframe)
    return AICostSummaryResponse.model_validate(summary)


@router.get(
    "/backups",
    response_model=BackupListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Database Backups",
    description="Retrieves existing backup snapshots with size, SHA-256 checksums, and retention window status.",
)
async def list_database_backups(
    backup_service: BackupService = Depends(get_backup_service),
) -> BackupListResponse:
    backups = await backup_service.list_backups()
    return BackupListResponse(
        total=len(backups),
        retention_days=backup_service.DEFAULT_RETENTION_DAYS,
        backups=[BackupMetadataResponse.model_validate(b) for b in backups],
    )


@router.post(
    "/backups/create",
    response_model=BackupMetadataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Atomic Database Snapshot Backup",
    description="Generates a cryptographically verified database snapshot and retention manifest.",
)
async def create_database_backup(
    payload: BackupCreateRequest,
    backup_service: BackupService = Depends(get_backup_service),
) -> BackupMetadataResponse:
    manifest = await backup_service.create_backup(
        backup_type=payload.backup_type,
        notes=payload.notes,
    )
    return BackupMetadataResponse.model_validate(manifest)


@router.post(
    "/backups/validate",
    response_model=BackupValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Backup Integrity",
    description="Audits SHA-256 integrity, file boundaries, and schema tables within a backup artifact.",
)
async def validate_database_backup(
    backup_id: str = Query(..., description="Unique backup identifier"),
    backup_service: BackupService = Depends(get_backup_service),
) -> BackupValidationResponse:
    report = await backup_service.validate_backup(backup_id=backup_id)
    return BackupValidationResponse.model_validate(report)


@router.post(
    "/backups/restore",
    response_model=BackupRestoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Restore Database from Backup",
    description="Executes a dry-run or live database restore from a verified snapshot.",
)
async def restore_database_backup(
    payload: BackupRestoreRequest,
    backup_service: BackupService = Depends(get_backup_service),
) -> BackupRestoreResponse:
    result = await backup_service.restore_backup(
        backup_id=payload.backup_id,
        dry_run=payload.dry_run,
        confirm=payload.confirm,
    )
    return BackupRestoreResponse.model_validate(result)


@router.get(
    "/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Inspect Background Task Status",
    description="Polls execution state, result, or error of an asynchronous background task.",
)
async def get_task_status(
    task_id: str,
    queue: BackgroundTaskQueue = Depends(get_task_queue),
):
    status_info = await queue.get_task_status(task_id)
    if not status_info:
        return {"task_id": task_id, "status": "UNKNOWN", "message": "Task not found."}
    return status_info


@router.post(
    "/files/validate",
    response_model=FileValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validate and Security-Scan Uploaded File",
    description="Performs in-line MIME magic byte checks, filename traversal sanitization, and malware scanning.",
)
async def validate_uploaded_file(
    file: UploadFile = File(...),
) -> FileValidationResult:
    content = await file.read()
    validator = FileSecurityValidator()
    is_clean, safe_name, sha256, scan_engine = validator.validate_and_scan(
        raw_data=content,
        filename=file.filename or "upload.pdf",
    )
    return FileValidationResult(
        is_valid=True,
        filename=safe_name,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        sha256_checksum=sha256,
        is_quarantined=False,
        malware_scan_clean=is_clean,
        scan_engine=scan_engine,
    )
