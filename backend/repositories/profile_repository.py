import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.profile import ProfileModel
from repositories.base import BaseRepository


class ProfileRepository(BaseRepository[ProfileModel]):
    """
    Profile repository managing candidate profile records.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ProfileModel, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[ProfileModel]:
        """Fetch profile for a specific user ID."""
        stmt = select(ProfileModel).where(ProfileModel.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
