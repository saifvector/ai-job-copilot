import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from core.dependencies import get_job_service
from schemas.common import ApiResponse
from schemas.job import (
    JobFilterParams,
    JobListResponse,
    JobResponse,
    JobSyncRequest,
    JobSyncResponse,
)
from services.job_service import JobService

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[JobListResponse],
    summary="List Jobs with Pagination and Basic Filtering",
    description="Retrieve paginated list of aggregated jobs with optional sorting and pagination.",
)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize", description="Items per page"),
    sort_by: str = Query("newest", alias="sortBy", description="Sorting criteria: newest, highest_salary, most_relevant"),
    role: Optional[str] = Query(None, description="Filter by job role or title"),
    location: Optional[str] = Query(None, description="Filter by location"),
    source: Optional[str] = Query(None, description="Filter by source (RemoteOK, Greenhouse, Lever, Wellfound)"),
    job_service: JobService = Depends(get_job_service),
) -> ApiResponse[JobListResponse]:
    params = JobFilterParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        role=role,
        location=location,
        source=source,
    )
    result = await job_service.search_jobs(params)
    return ApiResponse(
        data=result,
        message=f"Retrieved {len(result.items)} jobs out of {result.total} total.",
    )


@router.get(
    "/search",
    response_model=ApiResponse[JobListResponse],
    summary="Advanced Job Search Engine",
    description="Faceted search with multi-parameter filtering across role, location, source, skill, and salary.",
)
async def search_jobs(
    query: Optional[str] = Query(None, description="Free text query matching title, company, or description"),
    role: Optional[str] = Query(None, description="Target job title or role"),
    location: Optional[str] = Query(None, description="Geographic location or 'Remote'"),
    source: Optional[str] = Query(None, description="Origin job board source"),
    skill: Optional[str] = Query(None, description="Required skill name (e.g., Python, React)"),
    min_salary: Optional[float] = Query(None, alias="minSalary", description="Minimum annual salary threshold"),
    sort_by: str = Query("newest", alias="sortBy", description="Sort order: newest, highest_salary, most_relevant"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize", description="Items per page"),
    job_service: JobService = Depends(get_job_service),
) -> ApiResponse[JobListResponse]:
    params = JobFilterParams(
        query=query,
        role=role,
        location=location,
        source=source,
        skill=skill,
        min_salary=min_salary,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    result = await job_service.search_jobs(params)
    return ApiResponse(
        data=result,
        message=f"Found {result.total} jobs matching criteria.",
    )


@router.post(
    "/sync",
    response_model=ApiResponse[JobSyncResponse],
    status_code=status.HTTP_200_OK,
    summary="Synchronize Jobs from External Providers",
    description="Triggers the ingestion pipeline across providers: RemoteOK, Greenhouse, Lever, and Wellfound.",
)
async def sync_jobs(
    payload: Optional[JobSyncRequest] = None,
    job_service: JobService = Depends(get_job_service),
) -> ApiResponse[JobSyncResponse]:
    source = payload.source if payload else None
    limit = payload.limit_per_source if payload else 50

    sync_result = await job_service.sync_jobs(source=source, limit_per_source=limit)
    return ApiResponse(
        data=sync_result,
        message=sync_result.message,
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[JobResponse],
    summary="Get Job Details by ID",
    description="Fetch full job details including description, requirements, skills, and apply link.",
)
async def get_job_by_id(
    id: uuid.UUID,
    job_service: JobService = Depends(get_job_service),
) -> ApiResponse[JobResponse]:
    job = await job_service.get_job(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{id}' was not found.",
        )
    return ApiResponse(
        data=job,
        message="Job retrieved successfully.",
    )
