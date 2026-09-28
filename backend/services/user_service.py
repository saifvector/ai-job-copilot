import uuid
from typing import Optional
from core.exceptions import ConflictException, NotFoundException
from models.user import UserModel
from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserUpdate
from services.base import BaseService


class UserService(BaseService[UserModel, UserCreate, UserUpdate]):
    """
    User business logic service.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        super().__init__(repository=user_repo, resource_name="User")
        self.user_repo = user_repo

    async def create_user(self, user_in: UserCreate) -> UserModel:
        """Create user ensuring unique email address."""
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ConflictException(f"User with email '{user_in.email}' already exists.")
        return await self.user_repo.create(user_in)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Lookup user by email address."""
        return await self.user_repo.get_by_email(email)

    async def get_user_with_profile(self, user_id: uuid.UUID) -> UserModel:
        """Retrieve user with eagerly populated profile relation."""
        user = await self.user_repo.get_with_profile(user_id)
        if not user:
            raise NotFoundException(resource="User", identifier=str(user_id))
        return user
