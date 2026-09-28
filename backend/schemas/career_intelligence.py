import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class OutcomeType(str, Enum):
    INTERVIEW_RECEIVED = "InterviewReceived"
    ASSESSMENT_RECEIVED = "AssessmentReceived"
    OFFER_RECEIVED = "OfferReceived"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class OutcomeEventCreate(BaseModel):
    application_id: uuid.UUID
    outcome_type: OutcomeType
    occurred_at: Optional[datetime] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OutcomeEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    application_id: uuid.UUID
    outcome_type: str
    occurred_at: datetime
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    job_title: Optional[str] = None
    company: Optional[str] = None

    @field_validator("metadata", mode="before")
    @classmethod
    def parse_metadata(cls, v: Any) -> Optional[Dict[str, Any]]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v


class OutcomeEventListResponse(BaseModel):
    items: List[OutcomeEventResponse]
    total: int


class OutcomeAnalyticsSummary(BaseModel):
    total_applications: int = 0
    total_outcomes: int = 0
    interviews_received: int = 0
    assessments_received: int = 0
    offers_received: int = 0
    rejections_received: int = 0
    withdrawals: int = 0
    interview_rate: float = 0.0
    assessment_rate: float = 0.0
    offer_rate: float = 0.0
    rejection_rate: float = 0.0
    avg_response_days: float = 0.0
    median_response_days: float = 0.0
    active_funnel: Dict[str, int] = Field(default_factory=dict)


class ResumePerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tailored_resume_id: Optional[uuid.UUID] = None
    resume_title: Optional[str] = None
    target_role: Optional[str] = None
    ats_score: Optional[float] = 0.0
    applications_sent: int = 0
    interviews_received: int = 0
    offers_received: int = 0
    response_rate: float = 0.0
    interview_conversion_rate: float = 0.0
    updated_at: datetime


class ResumePerformanceListResponse(BaseModel):
    items: List[ResumePerformanceResponse]
    total: int


class SkillImpactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_name: str
    interviews_influenced: int = 0
    offers_influenced: int = 0
    average_match_score: float = 0.0
    correlation_score: float = 0.0
    sample_size: int = 0
    recommendation_weight: str = "MODERATE"
    updated_at: datetime


class SkillImpactListResponse(BaseModel):
    items: List[SkillImpactResponse]
    total: int
    disclaimer: str = (
        "Descriptive statistics represent empirical correlations observed within your application history. "
        "These metrics do not constitute causal guarantees for future hiring outcomes."
    )


class CompanyResponseMetric(BaseModel):
    company: str
    applications_sent: int = 0
    responses_received: int = 0
    interviews_count: int = 0
    offers_count: int = 0
    response_rate: float = 0.0
    interview_rate: float = 0.0
    avg_response_days: float = 0.0


class CompanyResponseAnalyticsResponse(BaseModel):
    companies: List[CompanyResponseMetric]
    total_companies: int


class ApplicationStrategyMetric(BaseModel):
    source_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    score_tier_breakdown: List[Dict[str, Any]] = Field(default_factory=list)
    weekly_cadence: List[Dict[str, Any]] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str = "STRATEGY"  # SKILL, RESUME, STRATEGY, ROLE
    title: str
    description: str
    evidence: str
    impact_level: str = "HIGH"  # HIGH, MEDIUM, LOW
    action_suggested: str
    confidence_score: float = 0.85


class CareerRecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    basis_data_points: int = 0


class TrendPoint(BaseModel):
    date: str
    applications: int = 0
    interviews: int = 0
    offers: int = 0
    response_rate: float = 0.0


class CohortPoint(BaseModel):
    cohort: str
    applications: int = 0
    interviews: int = 0
    conversion_rate: float = 0.0


class HistoricalTrendResponse(BaseModel):
    trends: List[TrendPoint] = Field(default_factory=list)
    cohorts: List[CohortPoint] = Field(default_factory=list)


class CareerIntelligenceSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    snapshot_date: datetime
    total_applications: int
    interview_rate: float
    offer_rate: float
    rejection_rate: float
    average_response_days: float
    metrics_payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    @field_validator("metrics_payload", mode="before")
    @classmethod
    def parse_metrics_payload(cls, v: Any) -> Optional[Dict[str, Any]]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return {}
        return v


class CareerIntelligenceOverviewResponse(BaseModel):
    analytics: OutcomeAnalyticsSummary
    top_resumes: List[ResumePerformanceResponse] = Field(default_factory=list)
    top_skills: List[SkillImpactResponse] = Field(default_factory=list)
    top_companies: List[CompanyResponseMetric] = Field(default_factory=list)
    strategy: ApplicationStrategyMetric
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    trends: List[TrendPoint] = Field(default_factory=list)
