import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from core.logging import get_logger
from models.audit_log import AuditLogModel
from repositories.audit_log_repository import AuditLogRepository

logger = get_logger("services.audit_log")


class AuditLogService:
    """
    Central service recording forensic audit trails for sensitive domain events:
    resume uploads, profile modifications, report generation, application status transitions,
    and authentication security events.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AuditLogRepository(session=session)

    async def log_action(
        self,
        action: str,
        resource: str,
        user_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        """Records an audit log entry."""
        log_entry = await self.repository.create_log(
            action=action,
            resource=resource,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        logger.info(
            f"[AuditLog] action={action} resource={resource} user_id={user_id} resource_id={resource_id}"
        )
        return log_entry

    async def list_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Queries audit logs with pagination and JSON deserialization of details."""
        models, total = await self.repository.list_logs(
            user_id=user_id,
            action=action,
            resource=resource,
            limit=limit,
            offset=offset,
        )
        serialized = []
        for m in models:
            det = None
            if m.details:
                try:
                    det = json.loads(m.details)
                except Exception:
                    det = {"raw": m.details}
            serialized.append({
                "id": m.id,
                "user_id": m.user_id,
                "action": m.action,
                "resource": m.resource,
                "resource_id": m.resource_id,
                "details": det,
                "ip_address": m.ip_address,
                "user_agent": m.user_agent,
                "created_at": m.created_at,
            })
        return serialized, total

    # Domain specific event helpers
    async def log_resume_upload(
        self,
        user_id: uuid.UUID,
        resume_id: str,
        filename: str,
        size_bytes: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        return await self.log_action(
            action="RESUME_UPLOAD",
            resource="resume",
            user_id=user_id,
            resource_id=resume_id,
            details={"filename": filename, "size_bytes": size_bytes},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_profile_update(
        self,
        user_id: uuid.UUID,
        updated_fields: List[str],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        return await self.log_action(
            action="PROFILE_UPDATE",
            resource="profile",
            user_id=user_id,
            resource_id=str(user_id),
            details={"updated_fields": updated_fields},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_report_generation(
        self,
        user_id: uuid.UUID,
        report_id: str,
        report_type: str,
        format_type: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        return await self.log_action(
            action="REPORT_GENERATION",
            resource="report",
            user_id=user_id,
            resource_id=report_id,
            details={"report_type": report_type, "format": format_type},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_application_change(
        self,
        user_id: uuid.UUID,
        application_id: str,
        old_status: Optional[str],
        new_status: str,
        job_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        return await self.log_action(
            action="APPLICATION_CHANGE",
            resource="application",
            user_id=user_id,
            resource_id=application_id,
            details={"old_status": old_status, "new_status": new_status, "job_id": job_id},
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_auth_event(
        self,
        user_id: Optional[uuid.UUID],
        event_name: str,
        token_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        event_details = {"event": event_name, "token_id": token_id}
        if details:
            event_details.update(details)
        return await self.log_action(
            action=event_name,
            resource="auth",
            user_id=user_id,
            resource_id=token_id,
            details=event_details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
