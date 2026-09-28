"""
TailoredResumeRepository for Phase 7 AI Resume Tailoring Engine.
Provides database access methods for TailoredResume entities.
Methods: create, update, findByUser, findByJob, findById, delete.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.tailored_resume import TailoredResumeModel
from repositories.base import BaseRepository


class TailoredResumeRepository(BaseRepository[TailoredResumeModel]):
    """
    Repository layer for managing TailoredResume entities in PostgreSQL.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TailoredResumeModel, session)

    async def create(self, data: Dict[str, Any]) -> TailoredResumeModel:
        """Create new TailoredResume record."""
        tailored_resume = TailoredResumeModel(**data)
        self.session.add(tailored_resume)
        await self.session.flush()
        await self.session.refresh(tailored_resume)
        return tailored_resume

    async def update(
        self,
        tailored_resume: TailoredResumeModel,
        data: Dict[str, Any],
    ) -> TailoredResumeModel:
        """Update existing TailoredResume record attributes."""
        for key, value in data.items():
            if hasattr(tailored_resume, key):
                setattr(tailored_resume, key, value)
        tailored_resume.updated_at = datetime.now(timezone.utc)
        self.session.add(tailored_resume)
        await self.session.flush()
        await self.session.refresh(tailored_resume)
        return tailored_resume

    async def findByUser(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 50,
        skip: int = 0,
    ) -> List[TailoredResumeModel]:
        """Find all tailored resumes for a user, ordered by creation date descending."""
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(TailoredResumeModel)
            .options(
                selectinload(TailoredResumeModel.job),
                selectinload(TailoredResumeModel.original_resume),
            )
            .where(TailoredResumeModel.user_id == uid)
            .order_by(desc(TailoredResumeModel.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def findByJob(
        self,
        job_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[TailoredResumeModel]:
        """Find the latest tailored resume for a specific job and user."""
        jid = uuid.UUID(str(job_id))
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(TailoredResumeModel)
            .options(
                selectinload(TailoredResumeModel.job),
                selectinload(TailoredResumeModel.original_resume),
            )
            .where(
                TailoredResumeModel.user_id == uid,
                TailoredResumeModel.job_id == jid,
            )
            .order_by(desc(TailoredResumeModel.created_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def findById(
        self,
        id: Union[uuid.UUID, str],
        user_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> Optional[TailoredResumeModel]:
        """Find a tailored resume by ID, optionally scoped to a user."""
        rid = uuid.UUID(str(id))
        stmt = (
            select(TailoredResumeModel)
            .options(
                selectinload(TailoredResumeModel.job),
                selectinload(TailoredResumeModel.original_resume),
            )
            .where(TailoredResumeModel.id == rid)
        )
        if user_id is not None:
            uid = uuid.UUID(str(user_id))
            stmt = stmt.where(TailoredResumeModel.user_id == uid)

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete(self, tailored_resume: TailoredResumeModel) -> None:
        """Delete a tailored resume record."""
        await self.session.delete(tailored_resume)
        await self.session.flush()
