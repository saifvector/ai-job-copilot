"""
AnalyticsRepository for Phase 6 Dashboard and Analytics Workspace.
Provides efficient database queries and aggregations for dashboard metrics,
trends, match distributions, and historical snapshots.
"""
import uuid
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.analytics_snapshot import AnalyticsSnapshotModel
from models.job import JobModel
from models.match_result import MatchResultModel
from repositories.base import BaseRepository


class AnalyticsRepository(BaseRepository[AnalyticsSnapshotModel]):
    """
    Repository for AnalyticsSnapshot persistence and aggregated metrics computation.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AnalyticsSnapshotModel, session)

    async def create_snapshot(self, snapshot_data: Dict[str, Any]) -> AnalyticsSnapshotModel:
        """Persist a new analytical snapshot record."""
        snapshot = AnalyticsSnapshotModel(**snapshot_data)
        self.session.add(snapshot)
        await self.session.flush()
        await self.session.refresh(snapshot)
        return snapshot

    async def get_latest_snapshot(
        self, user_id: Union[uuid.UUID, str]
    ) -> Optional[AnalyticsSnapshotModel]:
        """Fetch the most recent historical snapshot for delta calculation."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(AnalyticsSnapshotModel)
            .where(AnalyticsSnapshotModel.user_id == uid)
            .order_by(desc(AnalyticsSnapshotModel.created_at))
            .limit(1)
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_snapshots(
        self, user_id: Union[uuid.UUID, str], limit: int = 30
    ) -> List[AnalyticsSnapshotModel]:
        """Retrieve recent historical snapshots ordered by creation date ascending for trend lines."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(AnalyticsSnapshotModel)
            .where(AnalyticsSnapshotModel.user_id == uid)
            .order_by(AnalyticsSnapshotModel.created_at.asc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_match_distribution(
        self, user_id: Union[uuid.UUID, str]
    ) -> Dict[str, int]:
        """
        Aggregate match count across tier intervals in a single optimized query:
        - excellent: score >= 85
        - strong: 70 <= score < 85
        - moderate: 50 <= score < 70
        - weak: score < 50
        """
        uid = uuid.UUID(str(user_id))
        stmt = select(
            func.coalesce(
                func.sum(case((MatchResultModel.overall_score >= 85.0, 1), else_=0)), 0
            ).label("excellent"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (MatchResultModel.overall_score >= 70.0)
                            & (MatchResultModel.overall_score < 85.0),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("strong"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            (MatchResultModel.overall_score >= 50.0)
                            & (MatchResultModel.overall_score < 70.0),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("moderate"),
            func.coalesce(
                func.sum(case((MatchResultModel.overall_score < 50.0, 1), else_=0)), 0
            ).label("weak"),
            func.count(MatchResultModel.id).label("total"),
            func.coalesce(func.avg(MatchResultModel.overall_score), 0.0).label(
                "avg_score"
            ),
        ).where(MatchResultModel.user_id == uid)

        result = await self.session.execute(stmt)
        row = result.fetchone()

        if not row:
            return {
                "excellent": 0,
                "strong": 0,
                "moderate": 0,
                "weak": 0,
                "total": 0,
                "avg_score": 0.0,
            }

        return {
            "excellent": int(row.excellent),
            "strong": int(row.strong),
            "moderate": int(row.moderate),
            "weak": int(row.weak),
            "total": int(row.total),
            "avg_score": round(float(row.avg_score), 2),
        }

    async def get_total_jobs_available(self) -> int:
        """Get global total active job listings count."""
        stmt = select(func.count(JobModel.id))
        res = await self.session.execute(stmt)
        return int(res.scalar_one() or 0)

    async def get_top_matches(
        self, user_id: Union[uuid.UUID, str], limit: int = 10
    ) -> List[MatchResultModel]:
        """Fetch candidate top matches eagerly joining job relation."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(MatchResultModel)
            .options(selectinload(MatchResultModel.job))
            .where(MatchResultModel.user_id == uid)
            .order_by(desc(MatchResultModel.overall_score))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_all_matches_with_jobs(
        self, user_id: Union[uuid.UUID, str], limit: int = 200
    ) -> List[MatchResultModel]:
        """Fetch all matched opportunities with attached jobs for skill gap and location analytics."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(MatchResultModel)
            .options(
                selectinload(MatchResultModel.job).selectinload(JobModel.skills)
            )
            .where(MatchResultModel.user_id == uid)
            .order_by(desc(MatchResultModel.overall_score))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
