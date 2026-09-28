"""
Recruiter CRM API Endpoints for Phase 10.
Provides routes to manage recruiters, hiring managers, outreach history,
interactions, referrals, and networking analytics.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user_id, get_recruiter_service
from schemas.common import ApiResponse
from schemas.recruiter import (
    ContactInteractionCreateRequest,
    ContactInteractionResponse,
    NetworkingAnalyticsResponse,
    RecruiterCreateRequest,
    RecruiterDetailResponse,
    RecruiterListResponse,
    RecruiterResponse,
    RecruiterUpdateRequest,
    ReferralCreateRequest,
    ReferralResponse,
)
from services.recruiter_service import RecruiterService

router = APIRouter()


@router.post(
    "",
    response_model=ApiResponse[RecruiterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Recruiter / Networking Contact",
    description="Add a new recruiter, hiring manager, or professional networking contact to the CRM.",
)
async def create_recruiter(
    payload: RecruiterCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[RecruiterResponse]:
    recruiter = await service.createRecruiter(user_id=user_id, payload=payload)
    return ApiResponse(
        data=recruiter,
        message="Recruiter successfully added to CRM.",
    )


@router.get(
    "",
    response_model=ApiResponse[RecruiterListResponse],
    summary="List Recruiters & Contacts",
    description="Retrieve candidate's recruiters and networking contacts with search and company filters.",
)
async def list_recruiters(
    company: Optional[str] = Query(None, description="Filter by company name"),
    search: Optional[str] = Query(None, description="Search term matching name, company, title, or notes"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[RecruiterListResponse]:
    data = await service.listRecruiters(
        user_id=user_id,
        company=company,
        search=search,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        data=data,
        message="Recruiters retrieved successfully.",
    )


@router.get(
    "/analytics",
    response_model=ApiResponse[NetworkingAnalyticsResponse],
    summary="Get Networking & Outreach Analytics",
    description="Compute CRM analytics including recruiters contacted, response rate, referral success rate, and outreach volume.",
)
async def get_networking_analytics(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[NetworkingAnalyticsResponse]:
    analytics = await service.getNetworkingAnalytics(user_id=user_id)
    return ApiResponse(
        data=analytics,
        message="Networking analytics calculated successfully.",
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[RecruiterDetailResponse],
    summary="Get Recruiter Details & History",
    description="Inspect full recruiter profile including contact details, interaction timeline, referrals, and notes.",
)
async def get_recruiter(
    id: uuid.UUID,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[RecruiterDetailResponse]:
    recruiter = await service.getRecruiter(recruiter_id=id)
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recruiter with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=recruiter,
        message="Recruiter details retrieved successfully.",
    )


@router.patch(
    "/{id}",
    response_model=ApiResponse[RecruiterResponse],
    summary="Update Recruiter Details",
    description="Modify contact information, title, company, or notes for a recruiter.",
)
async def update_recruiter(
    id: uuid.UUID,
    payload: RecruiterUpdateRequest,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[RecruiterResponse]:
    updated = await service.updateRecruiter(recruiter_id=id, payload=payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recruiter with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=updated,
        message="Recruiter successfully updated.",
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[bool],
    summary="Delete Recruiter",
    description="Remove recruiter from CRM and cascade delete associated interactions and referrals.",
)
async def delete_recruiter(
    id: uuid.UUID,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[bool]:
    deleted = await service.deleteRecruiter(recruiter_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recruiter with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=True,
        message="Recruiter successfully deleted from CRM.",
    )


@router.post(
    "/{id}/interactions",
    response_model=ApiResponse[ContactInteractionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Log Contact Interaction",
    description="Record a message, email, referral touchpoint, call, or interview with this contact.",
)
async def add_interaction(
    id: uuid.UUID,
    payload: ContactInteractionCreateRequest,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[ContactInteractionResponse]:
    interaction = await service.addInteraction(recruiter_id=id, payload=payload)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recruiter with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=interaction,
        message="Interaction successfully recorded.",
    )


@router.get(
    "/{id}/history",
    response_model=ApiResponse[List[ContactInteractionResponse]],
    summary="Get Interaction History",
    description="Retrieve chronological log of touchpoints, messages, calls, and meetings with this recruiter.",
)
async def get_recruiter_history(
    id: uuid.UUID,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[List[ContactInteractionResponse]]:
    history = await service.getRecruiterHistory(recruiter_id=id)
    return ApiResponse(
        data=history,
        message="Interaction history retrieved successfully.",
    )


@router.post(
    "/{id}/referrals",
    response_model=ApiResponse[ReferralResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Request / Add Referral",
    description="Record a job referral through this recruiter or networking contact.",
)
async def add_referral(
    id: uuid.UUID,
    payload: ReferralCreateRequest,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[ReferralResponse]:
    referral = await service.addReferral(recruiter_id=id, payload=payload)
    if not referral:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recruiter with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=referral,
        message="Referral successfully logged.",
    )
