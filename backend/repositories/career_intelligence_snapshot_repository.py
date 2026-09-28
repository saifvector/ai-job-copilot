import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.career_intelligence_snapshot import CareerIntelligenceSnapshotModel
from repositories.base import BaseRepository


class CareerIntelligenceSnapshotRepository(BaseRepository[CareerIntelligenceSnapshotModel]):
    """
    Repository for storing and querying analytical snapshots in the data warehouse layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CareerIntelligenceSnapshotModel, session)

    async def create_snapshot(
        self,
        user_id: uuid.UUID,
        total_applications: int,
        interview_rate: float,
        offer_rate: float,
        rejection_rate: float,
        average_response_days: float,
        metrics_payload: Dict[str, Any],
        snapshot_date: Optional[datetime] = None,
    ) -> CareerIntelligenceSnapshotModel:
        """
        Record a historical snapshot for cohort and trend analysis.
        """
        snapshot = CareerIntelligenceSnapshotModel(
            user_id=user_id,
            snapshot_date=snapshot_date or datetime.now(timezone.utc),
            total_applications=total_applications,
            interview_rate=interview_rate,
            offer_rate=offer_rate,
            rejection_rate=rejection_rate,
            average_response_days=average_response_days,
            metrics_payload=json.dumps(metrics_payload),
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(snapshot)
        await self.session.flush()
        await self.session.refresh(snapshot)
        return snapshot

    async def get_user_snapshots(
        self,
        user_id: uuid.UUID,
        limit: int = 30,
    ) -> List[CareerIntelligenceSnapshotModel]:
        """
        Retrieve chronological snapshots for trend evaluation.
        """
        stmt = (
            select(CareerIntelligenceSnapshotModel)
            .where(CareerIntelligenceSnapshotModel.user_id == user_id)
            .order_by(desc(CareerIntelligenceSnapshotModel.snapshot_date))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
