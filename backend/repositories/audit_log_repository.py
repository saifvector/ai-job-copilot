import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.audit_log import AuditLogModel
from repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLogModel]):
    """
    Repository for storing and querying forensic security and compliance audit logs.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(model=AuditLogModel, session=session)

    async def create_log(
        self,
        action: str,
        resource: str,
        user_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogModel:
        """Persists a new immutable audit log entry."""
        details_str = json.dumps(details, default=str) if details else None
        log_entry = AuditLogModel(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details_str,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.create(log_entry)

    async def list_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[AuditLogModel], int]:
        """Queries filtered audit logs ordered with newest records first."""
        stmt = select(AuditLogModel)
        count_stmt = select(func.count()).select_from(AuditLogModel)

        if user_id:
            stmt = stmt.where(AuditLogModel.user_id == user_id)
            count_stmt = count_stmt.where(AuditLogModel.user_id == user_id)
        if action:
            stmt = stmt.where(AuditLogModel.action == action)
            count_stmt = count_stmt.where(AuditLogModel.action == action)
        if resource:
            stmt = stmt.where(AuditLogModel.resource == resource)
            count_stmt = count_stmt.where(AuditLogModel.resource == resource)

        stmt = stmt.order_by(desc(AuditLogModel.created_at)).limit(limit).offset(offset)

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        logs_res = await self.session.execute(stmt)
        items = list(logs_res.scalars().all())

        return items, total
