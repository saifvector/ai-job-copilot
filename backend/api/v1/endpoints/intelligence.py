import logging
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_authenticated_user_id, get_db
from schemas.career_intelligence import (
    ApplicationStrategyMetric,
    CareerIntelligenceOverviewResponse,
    CareerIntelligenceSnapshotResponse,
    CareerRecommendationResponse,
    CompanyResponseAnalyticsResponse,
    HistoricalTrendResponse,
    OutcomeAnalyticsSummary,
    OutcomeEventCreate,
    OutcomeEventListResponse,
    OutcomeEventResponse,
    ResumePerformanceListResponse,
    SkillImpactListResponse,
)
from services.career_intelligence_service import CareerIntelligenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["Career Intelligence & Outcome Learning"])


@router.get("/overview", response_model=CareerIntelligenceOverviewResponse)
async def get_career_intelligence_overview(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Get full career intelligence executive overview including outcome rates,
    top resumes, skill impacts, company conversions, strategy metrics, and recommendations.
    """
    service = CareerIntelligenceService(db)
    return await service.get_overview(user_id)


@router.get("/outcomes", response_model=OutcomeEventListResponse)
async def list_outcome_events(
    outcome_type: Optional[str] = Query(None, description="Filter by outcome type"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    List chronological outcome milestone events (Interviews, Assessments, Offers, Rejections).
    """
    service = CareerIntelligenceService(db)
    items = await service.get_user_outcomes(
        user_id=user_id,
        limit=limit,
        offset=offset,
        outcome_type=outcome_type,
    )
    total = await service.outcome_repo.count_user_events(user_id=user_id, outcome_type=outcome_type)
    return {"items": items, "total": total}


@router.post("/outcomes", response_model=OutcomeEventResponse, status_code=status.HTTP_201_CREATED)
async def record_outcome_event(
    body: OutcomeEventCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Record an application outcome event and update pipeline state.
    """
    service = CareerIntelligenceService(db)
    try:
        return await service.record_outcome(
            user_id=user_id,
            application_id=body.application_id,
            outcome_type=body.outcome_type.value,
            occurred_at=body.occurred_at,
            notes=body.notes,
            metadata=body.metadata,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to record outcome event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record application outcome event",
        )


@router.get("/analytics", response_model=OutcomeAnalyticsSummary)
async def get_outcome_analytics(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Calculate summary metrics: interview rate, offer rate, response times, and funnel stages.
    """
    service = CareerIntelligenceService(db)
    return await service.analyze_outcomes(user_id)


@router.get("/skills", response_model=SkillImpactListResponse)
async def get_skill_impact_analytics(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Retrieve skill impact analysis and descriptive correlation metrics with positive outcomes.
    """
    service = CareerIntelligenceService(db)
    return await service.calculate_skill_impact(user_id)


@router.get("/resumes", response_model=ResumePerformanceListResponse)
async def get_resume_performances(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Compare empirical performance and conversion rates across tailored resume versions.
    """
    service = CareerIntelligenceService(db)
    items = await service.calculate_resume_performance(user_id)
    return {"items": items, "total": len(items)}


@router.get("/companies", response_model=CompanyResponseAnalyticsResponse)
async def get_company_response_analytics(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Retrieve company-level response rates, turnaround times, and interview frequencies.
    """
    service = CareerIntelligenceService(db)
    return await service.get_company_response_analytics(user_id)


@router.get("/strategy", response_model=ApplicationStrategyMetric)
async def get_application_strategy_analytics(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Analyze application channels, match score distribution yield, and cadence telemetry.
    """
    service = CareerIntelligenceService(db)
    return await service.get_application_strategy_analytics(user_id)


@router.get("/recommendations", response_model=CareerRecommendationResponse)
async def get_career_recommendations(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Generate evidence-based strategic career recommendations grounded in observed outcome data.
    """
    service = CareerIntelligenceService(db)
    return await service.get_recommendations(user_id)


@router.get("/trends", response_model=HistoricalTrendResponse)
async def get_career_trends(
    days: int = Query(default=90, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Retrieve historical outcome trends and cohort conversion metrics.
    """
    service = CareerIntelligenceService(db)
    return await service.get_trends(user_id, days=days)


@router.post("/snapshots", response_model=CareerIntelligenceSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_career_intelligence_snapshot(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """
    Capture and persist an analytical snapshot into the Data Warehouse layer.
    """
    service = CareerIntelligenceService(db)
    return await service.create_snapshot(user_id)
