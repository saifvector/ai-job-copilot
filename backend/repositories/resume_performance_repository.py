import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.resume_performance import ResumePerformanceModel
from models.tailored_resume import TailoredResumeModel
from models.job import JobModel
from repositories.base import BaseRepository


class ResumePerformanceRepository(BaseRepository[ResumePerformanceModel]):
    """
    Repository for tracking and updating tailored resume conversion and performance metrics.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ResumePerformanceModel, session)

    async def get_by_tailored_resume_id(
        self,
        user_id: uuid.UUID,
        tailored_resume_id: uuid.UUID,
    ) -> Optional[ResumePerformanceModel]:
        """
        Find resume performance record by tailored_resume_id.
        """
        stmt = (
            select(ResumePerformanceModel)
            .where(
                ResumePerformanceModel.user_id == user_id,
                ResumePerformanceModel.tailored_resume_id == tailored_resume_id,
            )
            .options(
                selectinload(ResumePerformanceModel.tailored_resume).selectinload(TailoredResumeModel.job)
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert_performance(
        self,
        user_id: uuid.UUID,
        tailored_resume_id: uuid.UUID,
        applications_sent: int,
        interviews_received: int,
        offers_received: int,
    ) -> ResumePerformanceModel:
        """
        Insert or update performance metrics for a tailored resume.
        """
        perf = await self.get_by_tailored_resume_id(user_id, tailored_resume_id)
        response_rate = (interviews_received / applications_sent) if applications_sent > 0 else 0.0

        if not perf:
            perf = ResumePerformanceModel(
                user_id=user_id,
                tailored_resume_id=tailored_resume_id,
                applications_sent=applications_sent,
                interviews_received=interviews_received,
                offers_received=offers_received,
                response_rate=response_rate,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.session.add(perf)
        else:
            perf.applications_sent = applications_sent
            perf.interviews_received = interviews_received
            perf.offers_received = offers_received
            perf.response_rate = response_rate
            perf.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(perf)
        return perf

    async def get_user_performances(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> List[ResumePerformanceModel]:
        """
        Get all resume performance metrics for a user, sorted by response rate descending.
        """
        stmt = (
            select(ResumePerformanceModel)
            .where(ResumePerformanceModel.user_id == user_id)
            .options(
                selectinload(ResumePerformanceModel.tailored_resume).selectinload(TailoredResumeModel.job)
            )
            .order_by(desc(ResumePerformanceModel.response_rate), desc(ResumePerformanceModel.applications_sent))
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
