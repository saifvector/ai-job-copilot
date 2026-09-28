import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from core.dependencies import get_user_service
from schemas.common import ApiResponse, PaginatedResponse, PaginationMeta
from schemas.user import UserCreate, UserRead, UserUpdate, UserWithProfileRead
from services.user_service import UserService

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[UserRead]],
    summary="List Users",
    description="Retrieve paginated list of registered users.",
)
async def list_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    items, meta = await user_service.list_paginated(page=page, page_size=page_size)
    users_read = [UserRead.model_validate(u) for u in items]
    return ApiResponse(
        data=PaginatedResponse(
            items=users_read,
            pagination=PaginationMeta(**meta),
        ),
        message="Users retrieved successfully",
    )


@router.post(
    "",
    response_model=ApiResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create User",
    description="Register a new user account.",
)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    created = await user_service.create_user(user_in)
    return ApiResponse(
        data=UserRead.model_validate(created),
        message="User created successfully",
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserWithProfileRead],
    summary="Get User By ID",
    description="Retrieve user details and associated candidate profile.",
)
async def get_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    user = await user_service.get_user_with_profile(user_id)
    return ApiResponse(
        data=UserWithProfileRead.model_validate(user),
        message="User retrieved successfully",
    )


@router.put(
    "/{user_id}",
    response_model=ApiResponse[UserRead],
    summary="Update User",
    description="Update user account details.",
)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> Any:
    updated = await user_service.update(user_id, user_in)
    return ApiResponse(
        data=UserRead.model_validate(updated),
        message="User updated successfully",
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete User",
    description="Remove user account and cascade delete associated profile.",
)
async def delete_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
) -> None:
    await user_service.delete(user_id)
