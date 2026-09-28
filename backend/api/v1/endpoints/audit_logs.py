import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from core.dependencies import get_audit_log_service, get_authenticated_user_id
from schemas.audit_log import AuditLogListResponse, AuditLogResponse
from services.audit_log_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logging & Compliance"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Security and Compliance Audit Logs",
    description="Returns filtered and paginated immutable audit logs for resumes, profile updates, reports, and applications.",
)
async def list_audit_logs(
    user_id: Optional[uuid.UUID] = Query(None, description="Filter logs by user UUID"),
    action: Optional[str] = Query(None, description="Filter by event action (e.g. RESUME_UPLOAD, APPLICATION_CHANGE)"),
    resource: Optional[str] = Query(None, description="Filter by resource type"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Item offset"),
    audit_service: AuditLogService = Depends(get_audit_log_service),
) -> AuditLogListResponse:
    items, total = await audit_service.list_logs(
        user_id=user_id,
        action=action,
        resource=resource,
        limit=limit,
        offset=offset,
    )
    return AuditLogListResponse(
        total=total,
        items=[AuditLogResponse.model_validate(item) for item in items],
        limit=limit,
        offset=offset,
    )
