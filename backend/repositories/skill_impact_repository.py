import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.skill_impact import SkillImpactModel
from repositories.base import BaseRepository


class SkillImpactRepository(BaseRepository[SkillImpactModel]):
    """
    Repository for persisting and querying skill correlation metrics and impact scores.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SkillImpactModel, session)

    async def get_by_skill_name(
        self,
        user_id: uuid.UUID,
        skill_name: str,
    ) -> Optional[SkillImpactModel]:
        """
        Find skill impact record by skill name.
        """
        stmt = select(SkillImpactModel).where(
            SkillImpactModel.user_id == user_id,
            SkillImpactModel.skill_name.ilike(skill_name.strip()),
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def upsert_skill_impact(
        self,
        user_id: uuid.UUID,
        skill_name: str,
        interviews_influenced: int,
        offers_influenced: int,
        average_match_score: float,
    ) -> SkillImpactModel:
        """
        Upsert descriptive skill metrics.
        """
        record = await self.get_by_skill_name(user_id, skill_name)
        normalized_name = skill_name.strip()

        if not record:
            record = SkillImpactModel(
                user_id=user_id,
                skill_name=normalized_name,
                interviews_influenced=interviews_influenced,
                offers_influenced=offers_influenced,
                average_match_score=average_match_score,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.session.add(record)
        else:
            record.interviews_influenced = interviews_influenced
            record.offers_influenced = offers_influenced
            record.average_match_score = average_match_score
            record.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_user_skill_impacts(
        self,
        user_id: uuid.UUID,
        limit: int = 100,
    ) -> List[SkillImpactModel]:
        """
        Fetch all skill impact metrics for a user, sorted by interviews influenced descending.
        """
        stmt = (
            select(SkillImpactModel)
            .where(SkillImpactModel.user_id == user_id)
            .order_by(
                desc(SkillImpactModel.interviews_influenced),
                desc(SkillImpactModel.offers_influenced),
                desc(SkillImpactModel.average_match_score),
            )
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
