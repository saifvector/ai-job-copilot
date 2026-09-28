"""
Dashboard and Analytics API endpoints for AI Job Copilot.
Exposes high-performance REST APIs for dashboard summaries, profile health auditing,
career readiness diagnosis, skill gap analysis, and interactive chart datasets.
"""
import uuid
from fastapi import APIRouter, Depends, status

from core.dependencies import get_analytics_service, get_current_user_id
from schemas.analytics import (
    AnalyticsDashboardResponse,
    AnalyticsSnapshotItem,
    CareerReadinessResponse,
    DashboardOverviewResponse,
    ProfileHealthResponse,
    SkillGapAnalysisResponse,
)
from schemas.common import ApiResponse
from services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[DashboardOverviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Dashboard Overview",
    description="Retrieve high-level KPI cards, match distributions, score deltas, and Top 10 matches.",
)
async def get_dashboard_overview(
    user_id: uuid.UUID = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[DashboardOverviewResponse]:
    """Retrieve full dashboard KPI overview and top opportunities."""
    data = await analytics_service.generateDashboard(user_id=user_id)
    return ApiResponse(
        data=data,
        message="Dashboard overview loaded successfully",
    )


@router.get(
    "/profile-health",
    response_model=ApiResponse[ProfileHealthResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Profile Health Score",
    description="Calculates profile completeness across resume, skill, experience, and education pillars.",
)
async def get_profile_health(
    user_id: uuid.UUID = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[ProfileHealthResponse]:
    """Retrieve detailed profile health breakdown and enhancement recommendations."""
    data = await analytics_service.calculateProfileHealth(user_id=user_id)
    return ApiResponse(
        data=data,
        message="Profile health calculated successfully",
    )


@router.get(
    "/readiness",
    response_model=ApiResponse[CareerReadinessResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Career Readiness Score",
    description="Computes readiness rating based on resume quality, skills alignment, and market match rate.",
)
async def get_career_readiness(
    user_id: uuid.UUID = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[CareerReadinessResponse]:
    """Retrieve career readiness score and actionable strategic explanation."""
    data = await analytics_service.calculateCareerReadiness(user_id=user_id)
    return ApiResponse(
        data=data,
        message="Career readiness evaluated successfully",
    )


@router.get(
    "/skills",
    response_model=ApiResponse[SkillGapAnalysisResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Skill Gap Analysis",
    description="Identifies most requested skills, missing skills, and emerging market competencies.",
)
async def get_skill_gap_analysis(
    user_id: uuid.UUID = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[SkillGapAnalysisResponse]:
    """Analyze all matched opportunities to surface market skill demand and gaps."""
    data = await analytics_service.generateSkillGapAnalysis(user_id=user_id)
    return ApiResponse(
        data=data,
        message="Skill gap analysis generated successfully",
    )


@router.get(
    "/analytics",
    response_model=ApiResponse[AnalyticsDashboardResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Analytics Visualizations",
    description="Aggregates data for match distribution, top skills, missing skills, location, and progress charts.",
)
async def get_analytics_dashboard(
    user_id: uuid.UUID = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[AnalyticsDashboardResponse]:
    """Retrieve structured data ready for rendering Recharts visualizations."""
    data = await analytics_service.getAnalytics(user_id=user_id)
    return ApiResponse(
        data=data,
        message="Analytics visualization datasets compiled successfully",
    )


@router.post(
    "/snapshot",
    response_model=ApiResponse[AnalyticsSnapshotItem],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Analytics Snapshot",
    description="Capture and persist current metrics as a historical progress point.",
)
async def create_analytics_snapshot(
    user_id: uuid.UUID = Depends(get_current_user_id),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> ApiResponse[AnalyticsSnapshotItem]:
    """Create a persistent analytical checkpoint for trend monitoring."""
    snapshot = await analytics_service.generateAnalyticsSnapshot(user_id=user_id)
    snapshot_item = AnalyticsSnapshotItem(
        id=snapshot.id,
        timestamp=snapshot.created_at,
        profile_score=round(snapshot.profile_score, 1),
        readiness_score=round(snapshot.readiness_score, 1),
        average_match_score=round(snapshot.average_match_score, 1),
        excellent_matches=snapshot.excellent_matches,
        strong_matches=snapshot.strong_matches,
        moderate_matches=snapshot.moderate_matches,
        weak_matches=snapshot.weak_matches,
    )
    return ApiResponse(
        data=snapshot_item,
        message="Analytics snapshot recorded successfully",
    )
