import uuid
from typing import Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.resume import ResumeModel
from repositories.base import BaseRepository
from schemas.resume import ResumeCreate, ResumeUpdate


class ResumeRepository(BaseRepository[ResumeModel]):
    """
    Resume repository handling candidate resume database persistence.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ResumeModel, session)

    async def find_by_user(self, user_id: Union[uuid.UUID, str]) -> Optional[ResumeModel]:
        """
        Find resume record belonging to a specific user.
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        stmt = select(ResumeModel).where(ResumeModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # CamelCase alias matching user specification
    async def findByUser(self, user_id: Union[uuid.UUID, str]) -> Optional[ResumeModel]:
        return await self.find_by_user(user_id)

    async def delete_by_user(self, user_id: Union[uuid.UUID, str]) -> bool:
        """
        Delete resume record belonging to a specific user.
        """
        resume = await self.find_by_user(user_id)
        if resume:
            await self.session.delete(resume)
            await self.session.flush()
            return True
        return False
