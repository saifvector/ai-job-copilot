"""
ApplicationRepository for Phase 8 Application Tracking System.
Provides database access methods for Application entities, pipeline grouping,
and status transitions.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.application import ApplicationModel
from models.application_event import ApplicationEventModel
from models.interview import InterviewModel
from models.job import JobModel
from repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[ApplicationModel]):
    """
    Repository layer for managing Application entities in PostgreSQL.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ApplicationModel, session)

    async def create(self, data: Dict[str, Any]) -> ApplicationModel:
        """Create new Application record and initialize baseline event."""
        application = ApplicationModel(**data)
        self.session.add(application)
        await self.session.flush()
        await self.session.refresh(application)
        return application

    async def update(
        self,
        application: ApplicationModel,
        data: Dict[str, Any],
    ) -> ApplicationModel:
        """Update existing Application attributes."""
        for key, value in data.items():
            if hasattr(application, key):
                setattr(application, key, value)
        application.last_updated = datetime.now(timezone.utc)
        self.session.add(application)
        await self.session.flush()
        await self.session.refresh(application)
        return application

    async def findById(
        self,
        application_id: Union[uuid.UUID, str],
    ) -> Optional[ApplicationModel]:
        """Find application by ID with complete relationships loaded."""
        app_id = uuid.UUID(str(application_id))
        await self.session.flush()
        stmt = (
            select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.job),
                selectinload(ApplicationModel.tailored_resume),
                selectinload(ApplicationModel.events),
                selectinload(ApplicationModel.interviews),
            )
            .where(ApplicationModel.id == app_id)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def findByUserAndJob(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> Optional[ApplicationModel]:
        """Find application by user ID and target job ID."""
        uid = uuid.UUID(str(user_id))
        jid = uuid.UUID(str(job_id))
        stmt = (
            select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.job),
                selectinload(ApplicationModel.events),
                selectinload(ApplicationModel.interviews),
            )
            .where(
                and_(
                    ApplicationModel.user_id == uid,
                    ApplicationModel.job_id == jid,
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def findByUser(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[ApplicationModel]:
        """Find applications for user with optional status filter, sorted by last_updated descending."""
        uid = uuid.UUID(str(user_id))
        query = (
            select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.job),
                selectinload(ApplicationModel.events),
                selectinload(ApplicationModel.interviews),
            )
            .where(ApplicationModel.user_id == uid)
        )
        if status:
            query = query.where(ApplicationModel.status == status.upper())

        query = query.order_by(desc(ApplicationModel.last_updated)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def getPipeline(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> List[ApplicationModel]:
        """Retrieve all active and archived applications for candidate pipeline."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(ApplicationModel)
            .options(
                selectinload(ApplicationModel.job),
                selectinload(ApplicationModel.interviews),
            )
            .where(ApplicationModel.user_id == uid)
            .order_by(desc(ApplicationModel.last_updated))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def getStatusCounts(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> Dict[str, int]:
        """Get aggregate counts of applications grouped by status."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(ApplicationModel.status, func.count(ApplicationModel.id))
            .where(ApplicationModel.user_id == uid)
            .group_by(ApplicationModel.status)
        )
        result = await self.session.execute(stmt)
        counts = {
            "SAVED": 0,
            "APPLIED": 0,
            "ASSESSMENT": 0,
            "INTERVIEW": 0,
            "OFFER": 0,
            "REJECTED": 0,
            "WITHDRAWN": 0,
        }
        for status, count in result.all():
            counts[status] = count
        return counts

    async def getSourceCounts(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> Dict[str, int]:
        """Get aggregate counts of applications grouped by source."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(func.coalesce(ApplicationModel.source, "Direct / Manual"), func.count(ApplicationModel.id))
            .where(ApplicationModel.user_id == uid)
            .group_by(ApplicationModel.source)
        )
        result = await self.session.execute(stmt)
        return {source: count for source, count in result.all()}
