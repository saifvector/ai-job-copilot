"""
Resume Tailoring API Endpoints for Phase 7.
Provides routes to generate, list, inspect, and export job-specific tailored resumes.
"""
import urllib.parse
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status
from core.dependencies import get_current_user_id, get_resume_tailoring_service
from schemas.common import ApiResponse
from schemas.tailoring import (
    TailoredResumeCreateRequest,
    TailoredResumeListItem,
    TailoredResumeResponse,
)
from services.resume_tailoring_service import ResumeTailoringService

router = APIRouter()


@router.post(
    "/tailor",
    response_model=ApiResponse[TailoredResumeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Tailor Resume for Target Job",
    description=(
        "Analyzes target job description, performs keyword alignment, and generates 3 tailored resume "
        "variations (ATS, Recruiter, Balanced) using Gemini Pro with Flash fallback. "
        "Strictly enforces truthfulness (zero invented skills or experience) and calculates ATS score."
    ),
)
async def tailor_resume(
    payload: TailoredResumeCreateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ResumeTailoringService = Depends(get_resume_tailoring_service),
) -> ApiResponse[TailoredResumeResponse]:
    result = await service.generate_tailored_resume(
        user_id=user_id,
        job_id=payload.job_id,
        resume_id=payload.resume_id,
        target_version=payload.target_version or "balanced",
        custom_instructions=payload.custom_instructions,
    )
    return ApiResponse(
        data=result,
        message="Resume successfully tailored with multi-version ATS optimization.",
    )


@router.get(
    "/tailored",
    response_model=ApiResponse[List[TailoredResumeListItem]],
    summary="List Tailored Resumes",
    description="Retrieve list of all tailored resumes generated for the authenticated candidate.",
)
async def list_tailored_resumes(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ResumeTailoringService = Depends(get_resume_tailoring_service),
) -> ApiResponse[List[TailoredResumeListItem]]:
    items = await service.get_tailored_resumes(user_id=user_id)
    return ApiResponse(
        data=items,
        message="Tailored resumes retrieved successfully.",
    )


@router.get(
    "/tailored/{id}",
    response_model=ApiResponse[TailoredResumeResponse],
    summary="Get Tailored Resume by ID",
    description="Retrieve full tailored resume record including ATS score, keyword coverage, and all 3 versions.",
)
async def get_tailored_resume(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ResumeTailoringService = Depends(get_resume_tailoring_service),
) -> ApiResponse[TailoredResumeResponse]:
    result = await service.get_tailored_resume_by_id(user_id=user_id, tailored_id=id)
    return ApiResponse(
        data=result,
        message="Tailored resume retrieved successfully.",
    )


@router.get(
    "/tailored/{id}/export",
    summary="Export Tailored Resume Document",
    description=(
        "Exports the selected tailored resume version as a PDF, DOCX, or Markdown document. "
        "Returns binary file stream with appropriate Content-Disposition headers."
    ),
)
async def export_tailored_resume(
    id: uuid.UUID,
    format: str = Query(default="pdf", description="Export file format: 'pdf', 'docx', or 'markdown'"),
    version: str = Query(default="balanced", description="Resume version: 'ats', 'recruiter', or 'balanced'"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: ResumeTailoringService = Depends(get_resume_tailoring_service),
) -> Response:
    content, media_type, filename = await service.export_resume(
        user_id=user_id,
        tailored_id=id,
        format_type=format,
        version_type=version,
    )

    encoded_filename = urllib.parse.quote(filename)
    disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": disposition,
            "Content-Length": str(len(content)),
            "Cache-Control": "private, no-cache, no-store, must-revalidate",
        },
    )
