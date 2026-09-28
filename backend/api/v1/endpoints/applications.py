"""
Application Tracking System API Endpoints for Phase 8.
Provides routes to track, update, pipeline, and analyze job applications,
events, and scheduled interview rounds.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from core.dependencies import get_application_service, get_current_user_id
from schemas.application import (
    ApplicationAnalyticsResponse,
    ApplicationCreateRequest,
    ApplicationEventCreateRequest,
    ApplicationEventResponse,
    ApplicationListItem,
    ApplicationNotesUpdateRequest,
    ApplicationResponse,
    ApplicationStatusUpdateRequest,
    InterviewCreateRequest,
    InterviewResponse,
    PipelineResponse,
)
from schemas.common import ApiResponse
from services.application_service import ApplicationService

router = APIRouter()


@router.post(
    "",
    response_model=ApiResponse[ApplicationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Track or Create Job Application",
    description="Track a target job into candidate's application pipeline with initial status and notes.",
)
async def create_application(
    payload: ApplicationCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationResponse]:
    application = await service.create_application(user_id=user_id, request=payload)
    return ApiResponse(
        data=application,
        message="Application successfully tracked in pipeline.",
    )


@router.get(
    "",
    response_model=ApiResponse[List[ApplicationListItem]],
    summary="List Tracked Applications",
    description="Retrieve all tracked applications for candidate with optional status filtering.",
)
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status: SAVED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, REJECTED, WITHDRAWN"),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[List[ApplicationListItem]]:
    items = await service.list_applications(user_id=user_id, status=status, limit=limit, skip=skip)
    return ApiResponse(data=items)


@router.get(
    "/pipeline",
    response_model=ApiResponse[PipelineResponse],
    summary="Get Application Pipeline Kanban",
    description="Retrieve applications grouped by status column for the interactive Kanban board view.",
)
async def get_pipeline(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[PipelineResponse]:
    pipeline = await service.get_pipeline(user_id=user_id)
    return ApiResponse(data=pipeline)


@router.get(
    "/analytics",
    response_model=ApiResponse[ApplicationAnalyticsResponse],
    summary="Get Application Pipeline Analytics",
    description="Calculate application metrics, conversion funnels, interview rate, offer rate, and response rate.",
)
async def get_analytics(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationAnalyticsResponse]:
    analytics = await service.get_analytics(user_id=user_id)
    return ApiResponse(data=analytics)


@router.get(
    "/{id}",
    response_model=ApiResponse[ApplicationResponse],
    summary="Get Application Details",
    description="Retrieve complete application details, target job specifications, timeline events, and interview history.",
)
async def get_application(
    id: uuid.UUID,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationResponse]:
    application = await service.get_application_by_id(application_id=id)
    return ApiResponse(data=application)


@router.patch(
    "/{id}/status",
    response_model=ApiResponse[ApplicationResponse],
    summary="Update Application Status",
    description="Transition application to a new pipeline status (e.g. from APPLIED to INTERVIEW) and log event.",
)
async def update_status(
    id: uuid.UUID,
    payload: ApplicationStatusUpdateRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationResponse]:
    application = await service.update_status(
        application_id=id,
        new_status=payload.status,
        notes=payload.notes,
    )
    return ApiResponse(
        data=application,
        message=f"Application status updated to {payload.status}.",
    )


@router.patch(
    "/{id}/notes",
    response_model=ApiResponse[ApplicationResponse],
    summary="Update Application Notes",
    description="Update candidate private notes and recruiter information for the application.",
)
async def update_notes(
    id: uuid.UUID,
    payload: ApplicationNotesUpdateRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationResponse]:
    application = await service.update_notes(
        application_id=id,
        notes=payload.notes,
    )
    return ApiResponse(
        data=application,
        message="Application notes successfully updated.",
    )


@router.post(
    "/{id}/events",
    response_model=ApiResponse[ApplicationEventResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Application Timeline Event",
    description="Record a milestone or manual activity event to the chronological application audit timeline.",
)
async def add_event(
    id: uuid.UUID,
    payload: ApplicationEventCreateRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationEventResponse]:
    event = await service.add_event(application_id=id, request=payload)
    return ApiResponse(
        data=event,
        message="Timeline milestone event successfully recorded.",
    )


@router.post(
    "/{id}/interviews",
    response_model=ApiResponse[InterviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Schedule Interview Round",
    description="Schedule an interview round (HR, Technical, Managerial, Final), log timeline event, and advance status.",
)
async def add_interview(
    id: uuid.UUID,
    payload: InterviewCreateRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[InterviewResponse]:
    interview = await service.add_interview(application_id=id, request=payload)
    return ApiResponse(
        data=interview,
        message="Interview round successfully scheduled.",
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[bool],
    summary="Delete Application",
    description="Remove tracked application and cascade delete all associated events and interview records.",
)
async def delete_application(
    id: uuid.UUID,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[bool]:
    await service.delete_application(application_id=id)
    return ApiResponse(
        data=True,
        message="Application removed from tracking pipeline.",
    )
