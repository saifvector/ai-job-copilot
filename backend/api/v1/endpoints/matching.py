"""
Matching Engine API Endpoints for Candidate Job Fit Evaluation.
Provides routes to execute batch matching, retrieve paginated match results,
inspect single job match details with AI gap analysis, and fetch top matches.
"""
import math
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.dependencies import get_current_user_id, get_matching_service
from schemas.common import ApiResponse, PaginatedResponse, PaginationMeta
from schemas.matching import (
    MatchJobSnippet,
    MatchResultResponse,
    MatchRunRequest,
    MatchRunResponse,
)
from services.matching_service import MatchingService

router = APIRouter()


def _model_to_response(m) -> MatchResultResponse:
    """Helper to convert MatchResultModel into MatchResultResponse."""
    job_snippet = None
    if m.job:
        job_snippet = MatchJobSnippet(
            id=m.job.id,
            title=m.job.title,
            company=m.job.company,
            location=m.job.location,
            employment_type=m.job.employment_type,
            salary_min=m.job.salary_min,
            salary_max=m.job.salary_max,
            currency=m.job.currency,
            source=m.job.source,
            apply_url=m.job.apply_url,
            company_website=m.job.company_website,
            posted_at=m.job.posted_at,
            description=m.job.description,
            requirements=m.job.requirements,
        )

    return MatchResultResponse(
        id=m.id,
        user_id=m.user_id,
        job_id=m.job_id,
        overall_score=m.overall_score,
        skill_score=m.skill_score,
        experience_score=m.experience_score,
        education_score=m.education_score,
        location_score=m.location_score,
        role_score=m.role_score,
        strengths=m.strengths or [],
        missing_skills=m.missing_skills or [],
        recommendations=m.recommendations or [],
        generated_at=m.generated_at,
        updated_at=m.updated_at,
        job=job_snippet,
    )


@router.post(
    "/run",
    response_model=ApiResponse[MatchRunResponse],
    summary="Run AI Job Matching",
    description="Trigger asynchronous bulk matching against active jobs for the current candidate.",
)
async def run_matching(
    payload: Optional[MatchRunRequest] = None,
    user_id: uuid.UUID = Depends(get_current_user_id),
    matching_service: MatchingService = Depends(get_matching_service),
) -> ApiResponse[MatchRunResponse]:
    req = payload or MatchRunRequest()
    result = await matching_service.runMatching(
        user_id=user_id,
        job_ids=req.job_ids,
        limit=req.limit,
    )
    return ApiResponse(
        data=result,
        message=f"Matching completed: {result.matches_saved} jobs scored in {result.duration_ms}ms.",
    )


@router.get(
    "/results",
    response_model=ApiResponse[PaginatedResponse[MatchResultResponse]],
    summary="Get Match Results",
    description="Retrieve paginated candidate match results with faceted filters by score, location, company, and role.",
)
async def get_match_results(
    min_score: Optional[float] = Query(None, alias="minScore", ge=0.0, le=100.0, description="Minimum overall match score filter"),
    location: Optional[str] = Query(None, description="Location search filter"),
    company: Optional[str] = Query(None, description="Company name filter"),
    role: Optional[str] = Query(None, description="Role title filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize", description="Items per page"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    matching_service: MatchingService = Depends(get_matching_service),
) -> ApiResponse[PaginatedResponse[MatchResultResponse]]:
    skip = (page - 1) * page_size
    items, total = await matching_service.getMatchResults(
        user_id=user_id,
        min_score=min_score,
        location=location,
        company=company,
        role=role,
        skip=skip,
        limit=page_size,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    response_items = [_model_to_response(m) for m in items]

    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return ApiResponse(
        data=PaginatedResponse(items=response_items, pagination=pagination),
        message=f"Retrieved {len(response_items)} match results.",
    )


@router.get(
    "/top",
    response_model=ApiResponse[List[MatchResultResponse]],
    summary="Get Top Matches",
    description="Retrieve the highest-fit recommended jobs for the current candidate.",
)
async def get_top_matches(
    limit: int = Query(10, ge=1, le=50, description="Number of top matches to return"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    matching_service: MatchingService = Depends(get_matching_service),
) -> ApiResponse[List[MatchResultResponse]]:
    items = await matching_service.getTopMatches(user_id=user_id, limit=limit)
    response_items = [_model_to_response(m) for m in items]
    return ApiResponse(
        data=response_items,
        message=f"Retrieved top {len(response_items)} job matches.",
    )


@router.get(
    "/results/{job_id}",
    response_model=ApiResponse[MatchResultResponse],
    summary="Get Match Result for Job",
    description="Retrieve detailed score breakdown and AI gap analysis for a specific job.",
)
async def get_match_result_by_job(
    job_id: uuid.UUID,
    enrich_ai: bool = Query(False, alias="enrichAi", description="Trigger live Gemini Flash recommendation generation"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    matching_service: MatchingService = Depends(get_matching_service),
) -> ApiResponse[MatchResultResponse]:
    if enrich_ai:
        item = await matching_service.generateRecommendations(user_id=user_id, job_id=job_id)
    else:
        item = await matching_service.match_repo.findByUserAndJob(user_id=user_id, job_id=job_id)
        if not item:
            # Score on-the-fly if not scored yet
            await matching_service.scoreJob(user_id=user_id, job_id=job_id, generate_ai=False)
            item = await matching_service.match_repo.findByUserAndJob(user_id=user_id, job_id=job_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match result not found for job {job_id}",
        )

    return ApiResponse(
        data=_model_to_response(item),
        message="Match evaluation retrieved successfully.",
    )
