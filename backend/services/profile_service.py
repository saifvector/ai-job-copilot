import uuid
from typing import Optional
from core.exceptions import ConflictException, NotFoundException
from models.profile import ProfileModel
from repositories.profile_repository import ProfileRepository
from repositories.user_repository import UserRepository
from schemas.profile import ProfileCreate, ProfileUpdate
from services.base import BaseService


class ProfileService(BaseService[ProfileModel, ProfileCreate, ProfileUpdate]):
    """
    Candidate profile service managing preferences, roles, and years of experience.
    """

    def __init__(self, profile_repo: ProfileRepository, user_repo: UserRepository) -> None:
        super().__init__(repository=profile_repo, resource_name="Profile")
        self.profile_repo = profile_repo
        self.user_repo = user_repo

    async def get_by_user_id(self, user_id: uuid.UUID) -> ProfileModel:
        """Fetch profile belonging to a user or raise NotFoundException."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundException(resource="Profile for user", identifier=str(user_id))
        return profile

    async def create_profile(self, profile_in: ProfileCreate) -> ProfileModel:
        """Create new candidate profile validating user exists and does not already have a profile."""
        user = await self.user_repo.get_by_id(profile_in.user_id)
        if not user:
            raise NotFoundException(resource="User", identifier=str(profile_in.user_id))

        existing_profile = await self.profile_repo.get_by_user_id(profile_in.user_id)
        if existing_profile:
            raise ConflictException(f"Profile already exists for user {profile_in.user_id}.")

        return await self.profile_repo.create(profile_in)

    async def upsert_profile(self, user_id: uuid.UUID, profile_in: ProfileUpdate) -> ProfileModel:
        """Update existing profile or create if not present."""
        existing_profile = await self.profile_repo.get_by_user_id(user_id)
        if existing_profile:
            return await self.profile_repo.update(existing_profile, profile_in)

        # Create new profile
        create_payload = ProfileCreate(
            user_id=user_id,
            preferred_roles=profile_in.preferred_roles or [],
            preferred_locations=profile_in.preferred_locations or [],
            years_of_experience=profile_in.years_of_experience or 0,
            resume_url=profile_in.resume_url,
        )
        return await self.create_profile(create_payload)
