import uuid
from typing import Any
from fastapi import APIRouter, Depends, status
from core.dependencies import get_profile_service
from schemas.common import ApiResponse
from schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from services.profile_service import ProfileService

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=ApiResponse[ProfileRead],
    summary="Get Candidate Profile",
    description="Retrieve job preferences and profile data for a specific user.",
)
async def get_profile(
    user_id: uuid.UUID,
    profile_service: ProfileService = Depends(get_profile_service),
) -> Any:
    profile = await profile_service.get_by_user_id(user_id)
    return ApiResponse(
        data=ProfileRead.model_validate(profile),
        message="Profile retrieved successfully",
    )


@router.post(
    "",
    response_model=ApiResponse[ProfileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create Candidate Profile",
    description="Initialize a candidate profile with preferences for an existing user.",
)
async def create_profile(
    profile_in: ProfileCreate,
    profile_service: ProfileService = Depends(get_profile_service),
) -> Any:
    created = await profile_service.create_profile(profile_in)
    return ApiResponse(
        data=ProfileRead.model_validate(created),
        message="Profile created successfully",
    )


@router.put(
    "/{user_id}",
    response_model=ApiResponse[ProfileRead],
    summary="Upsert Profile",
    description="Update or initialize candidate job search preferences.",
)
async def upsert_profile(
    user_id: uuid.UUID,
    profile_in: ProfileUpdate,
    profile_service: ProfileService = Depends(get_profile_service),
) -> Any:
    updated = await profile_service.upsert_profile(user_id, profile_in)
    return ApiResponse(
        data=ProfileRead.model_validate(updated),
        message="Profile saved successfully",
    )
