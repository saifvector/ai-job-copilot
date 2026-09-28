import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.outcome_event import OutcomeEventModel
from models.application import ApplicationModel
from models.job import JobModel
from repositories.base import BaseRepository


class OutcomeEventRepository(BaseRepository[OutcomeEventModel]):
    """
    Repository for managing outcome milestone events (Interviews, Offers, Assessments, Rejections).
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(OutcomeEventModel, session)

    async def record_event(
        self,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
        outcome_type: str,
        occurred_at: Optional[datetime] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OutcomeEventModel:
        """
        Record a new outcome milestone event.
        """
        event = OutcomeEventModel(
            user_id=user_id,
            application_id=application_id,
            outcome_type=outcome_type,
            occurred_at=occurred_at or datetime.now(timezone.utc),
            notes=notes,
            metadata_payload=json.dumps(metadata) if metadata else None,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(event)
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def get_user_events(
        self,
        user_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
        outcome_type: Optional[str] = None,
    ) -> List[OutcomeEventModel]:
        """
        Fetch outcome events for a user with application and job relationship preloaded.
        """
        stmt = (
            select(OutcomeEventModel)
            .where(OutcomeEventModel.user_id == user_id)
            .options(
                selectinload(OutcomeEventModel.application).selectinload(ApplicationModel.job)
            )
            .order_by(desc(OutcomeEventModel.occurred_at))
            .limit(limit)
            .offset(offset)
        )
        if outcome_type:
            stmt = stmt.where(OutcomeEventModel.outcome_type == outcome_type)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def count_user_events(
        self,
        user_id: uuid.UUID,
        outcome_type: Optional[str] = None,
    ) -> int:
        """
        Count total outcome events for a user.
        """
        stmt = select(func.count(OutcomeEventModel.id)).where(OutcomeEventModel.user_id == user_id)
        if outcome_type:
            stmt = stmt.where(OutcomeEventModel.outcome_type == outcome_type)
        res = await self.session.execute(stmt)
        return res.scalar_one() or 0

    async def get_outcome_counts_by_type(
        self,
        user_id: uuid.UUID,
    ) -> Dict[str, int]:
        """
        Aggregate count of events grouped by outcome_type.
        """
        stmt = (
            select(OutcomeEventModel.outcome_type, func.count(OutcomeEventModel.id))
            .where(OutcomeEventModel.user_id == user_id)
            .group_by(OutcomeEventModel.outcome_type)
        )
        res = await self.session.execute(stmt)
        return {row[0]: row[1] for row in res.all()}

    async def get_events_for_application(
        self,
        application_id: uuid.UUID,
    ) -> List[OutcomeEventModel]:
        """
        Fetch all outcome events for a given application.
        """
        stmt = (
            select(OutcomeEventModel)
            .where(OutcomeEventModel.application_id == application_id)
            .order_by(desc(OutcomeEventModel.occurred_at))
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
