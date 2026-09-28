"""
FastAPI Routes for Phase 12 Application Assistant Platform.
Provides endpoints for:
- POST  /api/v1/application-assistant/create -> Create or retrieve draft
- GET   /api/v1/application-assistant/analytics -> Performance & draft analytics
- GET   /api/v1/application-assistant/drafts -> List user application drafts
- GET   /api/v1/application-assistant/{id} -> Inspect application draft by ID
- POST  /api/v1/application-assistant/generate-answers -> Generate truthful AI responses
- PATCH /api/v1/application-assistant/review -> Candidate review & edits
- POST  /api/v1/application-assistant/{id}/submit -> Candidate explicit submission
- GET   /api/v1/application-assistant/{id}/checklist -> Application readiness checklist
- DELETE /api/v1/application-assistant/{id} -> Delete application draft
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from core.dependencies import (
    get_application_assistant_service,
    get_current_user_id,
)
from schemas.application_assistant import (
    ApplicationDraftCreateRequest,
    ApplicationDraftResponse,
    AssistantAnalyticsResponse,
    ChecklistResponse,
    GenerateAnswersRequest,
    ReviewDraftRequest,
)
from schemas.common import ApiResponse
from services.application_assistant_service import ApplicationAssistantService

router = APIRouter()


@router.post(
    "/create",
    response_model=ApiResponse[ApplicationDraftResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Application Draft",
    description="Initiates an application draft for a target job, selects the initial resume, and seeds questions.",
)
async def create_application_draft(
    payload: ApplicationDraftCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[ApplicationDraftResponse]:
    draft = await service.create_draft(user_id=user_id, payload=payload)
    return ApiResponse(
        data=draft,
        message="Application draft initialized successfully.",
    )


@router.get(
    "/analytics",
    response_model=ApiResponse[AssistantAnalyticsResponse],
    status_code=status.HTTP_200_OK,
    summary="Application Assistant Analytics",
    description="Calculates application draft metrics including total drafts, completed submissions, and completion time.",
)
async def get_assistant_analytics(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[AssistantAnalyticsResponse]:
    analytics = await service.get_analytics(user_id=user_id)
    return ApiResponse(
        data=analytics,
        message="Application assistant analytics retrieved successfully.",
    )


@router.get(
    "/drafts",
    response_model=ApiResponse[List[ApplicationDraftResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Application Drafts",
    description="Retrieves candidate's application drafts with optional status filter.",
)
async def list_application_drafts(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[List[ApplicationDraftResponse]]:
    drafts = await service.list_drafts(
        user_id=user_id,
        limit=limit,
        offset=offset,
        status=status_filter,
    )
    return ApiResponse(
        data=drafts,
        message=f"Retrieved {len(drafts)} application draft(s).",
    )


@router.post(
    "/generate-answers",
    response_model=ApiResponse[ApplicationDraftResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Application Answers",
    description="Uses Gemini 2.5 Pro to generate 100% truthful answers grounded in candidate resume and target job requirements.",
)
async def generate_answers(
    payload: GenerateAnswersRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[ApplicationDraftResponse]:
    draft = await service.generate_answers(user_id=user_id, payload=payload)
    return ApiResponse(
        data=draft,
        message="AI responses generated successfully. Please review and confirm accuracy.",
    )


@router.patch(
    "/review",
    response_model=ApiResponse[ApplicationDraftResponse],
    status_code=status.HTTP_200_OK,
    summary="Review Application Draft",
    description="Candidate reviews, edits, and confirms generated answers and document selection. System never bypasses review.",
)
async def review_draft(
    payload: ReviewDraftRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[ApplicationDraftResponse]:
    draft = await service.review_draft(user_id=user_id, payload=payload)
    return ApiResponse(
        data=draft,
        message="Application review and answer edits saved successfully.",
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[ApplicationDraftResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Application Draft",
    description="Inspects an application draft by ID with eager-loaded questions and checklist.",
)
async def get_application_draft(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[ApplicationDraftResponse]:
    draft = await service.get_draft(user_id=user_id, draft_id=id)
    return ApiResponse(
        data=draft,
        message="Application draft retrieved successfully.",
    )


@router.get(
    "/{id}/checklist",
    response_model=ApiResponse[ChecklistResponse],
    status_code=status.HTTP_200_OK,
    summary="Evaluate Application Checklist",
    description="Calculates application readiness score and identifies missing fields.",
)
async def get_draft_checklist(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[ChecklistResponse]:
    checklist = await service.validate_draft(user_id=user_id, draft_id=id)
    return ApiResponse(
        data=checklist,
        message=f"Checklist generated: {checklist.readiness_score}% readiness score.",
    )


@router.post(
    "/{id}/submit",
    response_model=ApiResponse[ApplicationDraftResponse],
    status_code=status.HTTP_200_OK,
    summary="Candidate Explicit Submission Confirmation",
    description="Marks the draft as SubmittedByUser after manual review. System does not perform automatic browser submission.",
)
async def submit_application_draft(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[ApplicationDraftResponse]:
    draft = await service.submit_draft(user_id=user_id, draft_id=id)
    return ApiResponse(
        data=draft,
        message="Application successfully marked as submitted by candidate.",
    )


@router.delete(
    "/{id}",
    response_model=ApiResponse[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete Application Draft",
    description="Deletes an application draft and its associated questions.",
)
async def delete_application_draft(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ApplicationAssistantService = Depends(get_application_assistant_service),
) -> ApiResponse[bool]:
    success = await service.delete_draft(user_id=user_id, draft_id=id)
    return ApiResponse(
        data=success,
        message="Application draft deleted successfully." if success else "Draft not found.",
    )
