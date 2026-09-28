"""
ApplicationEventRepository for Phase 8 Application Tracking System.
Manages persistent chronological event audit trails for job applications.
"""
import uuid
from typing import Any, Dict, List, Union
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.application_event import ApplicationEventModel
from repositories.base import BaseRepository


class ApplicationEventRepository(BaseRepository[ApplicationEventModel]):
    """
    Repository for managing ApplicationEvent audit trail records.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ApplicationEventModel, session)

    async def create(self, data: Dict[str, Any]) -> ApplicationEventModel:
        """Create new ApplicationEvent milestone entry."""
        event = ApplicationEventModel(**data)
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def findByApplication(
        self,
        application_id: Union[uuid.UUID, str],
    ) -> List[ApplicationEventModel]:
        """Find all timeline events for a given application ordered chronologically descending."""
        app_id = uuid.UUID(str(application_id))
        stmt = (
            select(ApplicationEventModel)
            .where(ApplicationEventModel.application_id == app_id)
            .order_by(desc(ApplicationEventModel.created_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
