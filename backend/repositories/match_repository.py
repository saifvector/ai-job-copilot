"""
MatchRepository for Phase 5 AI Job Matching Engine.
Provides database access methods for MatchResult entities.
Methods: create, update, findByUser, findTopMatches, findByUserAndJob, bulk_upsert_matches.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.matching.base import MatchBreakdownDTO
from models.job import JobModel
from models.match_result import MatchResultModel
from repositories.base import BaseRepository


class MatchRepository(BaseRepository[MatchResultModel]):
    """
    Repository layer for managing MatchResult models in PostgreSQL.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MatchResultModel, session)

    async def create(self, match_data: Dict[str, Any]) -> MatchResultModel:
        """Create new MatchResult record."""
        match_result = MatchResultModel(**match_data)
        self.session.add(match_result)
        await self.session.flush()
        await self.session.refresh(match_result)
        return match_result

    async def update(
        self,
        match_result: MatchResultModel,
        update_data: Dict[str, Any],
    ) -> MatchResultModel:
        """Update existing MatchResult attributes."""
        for key, value in update_data.items():
            if hasattr(match_result, key):
                setattr(match_result, key, value)
        match_result.updated_at = datetime.now(timezone.utc)
        self.session.add(match_result)
        await self.session.flush()
        await self.session.refresh(match_result)
        return match_result

    async def findByUserAndJob(
        self,
        user_id: Union[uuid.UUID, str],
        job_id: Union[uuid.UUID, str],
    ) -> Optional[MatchResultModel]:
        """Find match result for specific user and job pair."""
        uid = uuid.UUID(str(user_id))
        jid = uuid.UUID(str(job_id))
        stmt = (
            select(MatchResultModel)
            .options(selectinload(MatchResultModel.job))
            .where(
                MatchResultModel.user_id == uid,
                MatchResultModel.job_id == jid,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def findByUser(
        self,
        user_id: Union[uuid.UUID, str],
        min_score: Optional[float] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[MatchResultModel], int]:
        """
        Query match results for a user with optional faceted filters, sorting, and pagination.
        """
        uid = uuid.UUID(str(user_id))
        query = (
            select(MatchResultModel)
            .join(JobModel, MatchResultModel.job_id == JobModel.id)
            .options(selectinload(MatchResultModel.job))
            .where(MatchResultModel.user_id == uid)
        )

        if min_score is not None and min_score > 0:
            query = query.where(MatchResultModel.overall_score >= min_score)

        if location:
            loc_pattern = f"%{location.strip()}%"
            query = query.where(JobModel.location.ilike(loc_pattern))

        if company:
            comp_pattern = f"%{company.strip()}%"
            query = query.where(JobModel.company.ilike(comp_pattern))

        if role:
            role_pattern = f"%{role.strip()}%"
            query = query.where(
                or_(
                    JobModel.title.ilike(role_pattern),
                    JobModel.description.ilike(role_pattern),
                )
            )

        # Count total matching records
        count_stmt = select(func.count()).select_from(query.subquery())
        total_count = (await self.session.execute(count_stmt)).scalar() or 0

        # Order by highest overall score first
        query = query.order_by(desc(MatchResultModel.overall_score), desc(MatchResultModel.generated_at))
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total_count

    async def findTopMatches(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 10,
    ) -> List[MatchResultModel]:
        """Fetch top highest-scoring job matches for a user."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(MatchResultModel)
            .options(selectinload(MatchResultModel.job))
            .where(MatchResultModel.user_id == uid)
            .order_by(desc(MatchResultModel.overall_score), desc(MatchResultModel.generated_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def bulk_upsert_matches(
        self,
        user_id: Union[uuid.UUID, str],
        matches: List[MatchBreakdownDTO],
    ) -> int:
        """
        Bulk upserts match results for a user in batches.
        Updates existing rows and creates new records.
        """
        if not matches:
            return 0

        uid = uuid.UUID(str(user_id))
        job_ids = [m.job_id for m in matches]

        # Fetch existing match results for this user & job batch
        existing_stmt = select(MatchResultModel).where(
            MatchResultModel.user_id == uid,
            MatchResultModel.job_id.in_(job_ids),
        )
        existing_res = await self.session.execute(existing_stmt)
        existing_map = {m.job_id: m for m in existing_res.scalars().all()}

        count = 0
        now = datetime.now(timezone.utc)

        for m in matches:
            if m.job_id in existing_map:
                # Update existing
                row = existing_map[m.job_id]
                row.overall_score = m.overall_score
                row.skill_score = m.skill_score
                row.experience_score = m.experience_score
                row.education_score = m.education_score
                row.location_score = m.location_score
                row.role_score = m.role_score
                row.strengths = m.strengths
                row.missing_skills = m.missing_skills
                row.recommendations = m.recommendations
                row.updated_at = now
            else:
                # Create new
                new_row = MatchResultModel(
                    user_id=uid,
                    job_id=m.job_id,
                    overall_score=m.overall_score,
                    skill_score=m.skill_score,
                    experience_score=m.experience_score,
                    education_score=m.education_score,
                    location_score=m.location_score,
                    role_score=m.role_score,
                    strengths=m.strengths,
                    missing_skills=m.missing_skills,
                    recommendations=m.recommendations,
                    generated_at=now,
                    updated_at=now,
                )
                self.session.add(new_row)
            count += 1

        await self.session.flush()
        return count
