import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.user import UserModel
from repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """
    User repository handling user-specific queries and database operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(UserModel, session)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Look up user by exact email address."""
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_profile(self, user_id: uuid.UUID) -> Optional[UserModel]:
        """Fetch user eagerly loading their associated 1-to-1 profile."""
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(selectinload(UserModel.profile))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
