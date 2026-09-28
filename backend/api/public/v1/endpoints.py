import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_db
from core.security.api_keys import ApiKeyContext, require_api_key
from schemas.public_api import (
    PublicApplicationCreateRequest,
    PublicApplicationListResponse,
    PublicApplicationResponse,
    PublicMatchListResponse,
    PublicMatchResponse,
    PublicProfileResponse,
    PublicReportListResponse,
    PublicReportResponse,
    PublicResumeListResponse,
    PublicResumeResponse,
)
from services.api_analytics_service import ApiAnalyticsService
from services.public_api_service import PublicApiService

router = APIRouter(tags=["Public API v1"])


async def _log_public_api_call(
    request: Request,
    db: AsyncSession,
    ctx: ApiKeyContext,
    status_code: int,
):
    try:
        latency_ms = round((time.perf_counter() - ctx.start_time) * 1000, 2)
        analytics_service = ApiAnalyticsService(db)
        await analytics_service.log_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=status_code,
            latency_ms=latency_ms,
            user_id=ctx.user_id,
            api_key_id=ctx.key_id,
            ip_address=request.client.host if request.client else None,
        )
    except Exception:
        pass


@router.get("/profile", response_model=PublicProfileResponse)
async def get_profile(
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:profile"])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve verified candidate profile summary, roles, and skills via API key."""
    service = PublicApiService(db)
    profile = await service.get_profile(ctx.user_id)
    if not profile:
        await _log_public_api_call(request, db, ctx, 404)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    await _log_public_api_call(request, db, ctx, 200)
    return profile


@router.get("/resumes", response_model=PublicResumeListResponse)
async def list_resumes(
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:resume"])),
    db: AsyncSession = Depends(get_db),
):
    """List uploaded resumes and associated skills."""
    service = PublicApiService(db)
    items = await service.list_resumes(ctx.user_id)
    await _log_public_api_call(request, db, ctx, 200)
    return {"items": items, "total": len(items)}


@router.get("/resumes/{resume_id}", response_model=PublicResumeResponse)
async def get_resume(
    resume_id: uuid.UUID,
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:resume"])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve metadata for a specific resume."""
    service = PublicApiService(db)
    resume = await service.get_resume(ctx.user_id, resume_id)
    if not resume:
        await _log_public_api_call(request, db, ctx, 404)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    await _log_public_api_call(request, db, ctx, 200)
    return resume


@router.get("/matches", response_model=PublicMatchListResponse)
async def list_matches(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:matches"])),
    db: AsyncSession = Depends(get_db),
):
    """Query AI matching scores, strengths, and gap recommendations."""
    service = PublicApiService(db)
    items, total = await service.list_matches(ctx.user_id, limit=limit, offset=offset)
    await _log_public_api_call(request, db, ctx, 200)
    return {"items": items, "total": total}


@router.get("/matches/{job_id}", response_model=PublicMatchResponse)
async def get_match_by_job(
    job_id: uuid.UUID,
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:matches"])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve match score and breakdown for a target job."""
    service = PublicApiService(db)
    match = await service.get_match_by_job(ctx.user_id, job_id)
    if not match:
        await _log_public_api_call(request, db, ctx, 404)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match result not found for this job")

    await _log_public_api_call(request, db, ctx, 200)
    return match


@router.get("/applications", response_model=PublicApplicationListResponse)
async def list_applications(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:applications"])),
    db: AsyncSession = Depends(get_db),
):
    """List job applications tracked for this account."""
    service = PublicApiService(db)
    items, total = await service.list_applications(ctx.user_id, limit=limit, offset=offset)
    await _log_public_api_call(request, db, ctx, 200)
    return {"items": items, "total": total}


@router.post("/applications", response_model=PublicApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    body: PublicApplicationCreateRequest,
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["write:applications"])),
    db: AsyncSession = Depends(get_db),
):
    """Record a new application submission and trigger application.created webhook."""
    service = PublicApiService(db)
    try:
        app = await service.create_application(
            user_id=ctx.user_id,
            job_id=body.job_id,
            resume_id=body.resume_id,
            status=body.status or "Applied",
            notes=body.notes,
        )
        await _log_public_api_call(request, db, ctx, 201)
        return app
    except ValueError as e:
        await _log_public_api_call(request, db, ctx, 400)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/applications/{application_id}", response_model=PublicApplicationResponse)
async def get_application(
    application_id: uuid.UUID,
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:applications"])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details and status for a specific application."""
    service = PublicApiService(db)
    app = await service.get_application(ctx.user_id, application_id)
    if not app:
        await _log_public_api_call(request, db, ctx, 404)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    await _log_public_api_call(request, db, ctx, 200)
    return app


@router.get("/reports", response_model=PublicReportListResponse)
async def list_reports(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:reports"])),
    db: AsyncSession = Depends(get_db),
):
    """List career intelligence reports."""
    service = PublicApiService(db)
    items, total = await service.list_reports(ctx.user_id, limit=limit, offset=offset)
    await _log_public_api_call(request, db, ctx, 200)
    return {"items": items, "total": total}


@router.get("/reports/{report_id}", response_model=PublicReportResponse)
async def get_report(
    report_id: uuid.UUID,
    request: Request,
    ctx: ApiKeyContext = Depends(require_api_key(required_scopes=["read:reports"])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details for a specific generated report."""
    service = PublicApiService(db)
    report = await service.get_report(ctx.user_id, report_id)
    if not report:
        await _log_public_api_call(request, db, ctx, 404)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    await _log_public_api_call(request, db, ctx, 200)
    return report
