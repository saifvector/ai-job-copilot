"""
Referral Tracker API Endpoints for Phase 10.
Provides routes to query, update status, and manage job referrals across recruiters.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user_id, get_recruiter_service
from schemas.common import ApiResponse
from schemas.recruiter import ReferralResponse, ReferralUpdateRequest
from services.recruiter_service import RecruiterService

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[List[ReferralResponse]],
    summary="List Referrals",
    description="Retrieve all referrals across contacts with optional status and company filtering.",
)
async def list_referrals(
    status: Optional[str] = Query(None, description="Filter by status: Requested, Received, Declined, Pending"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[List[ReferralResponse]]:
    referrals = await service.listReferrals(
        user_id=user_id,
        status=status,
        company=company,
    )
    return ApiResponse(
        data=referrals,
        message="Referrals retrieved successfully.",
    )


@router.patch(
    "/{id}",
    response_model=ApiResponse[ReferralResponse],
    summary="Update Referral Status & Details",
    description="Update the lifecycle status (Requested -> Received, Declined, Pending) or notes for a referral.",
)
async def update_referral(
    id: uuid.UUID,
    payload: ReferralUpdateRequest,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[ReferralResponse]:
    updated = await service.updateReferral(referral_id=id, payload=payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Referral with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=updated,
        message="Referral successfully updated.",
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[bool],
    summary="Delete Referral",
    description="Delete a referral record.",
)
async def delete_referral(
    id: uuid.UUID,
    service: RecruiterService = Depends(get_recruiter_service),
) -> ApiResponse[bool]:
    deleted = await service.deleteReferral(referral_id=id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Referral with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=True,
        message="Referral successfully deleted.",
    )
