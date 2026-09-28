"""
Pydantic schemas for Phase 6 Dashboard and Analytics Workspace.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MatchInsightItem(BaseModel):
    """Top match item formatted for Match Insights table and preview cards."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    job_id: uuid.UUID = Field(alias="jobId")
    job_title: str = Field(alias="jobTitle")
    company: str
    match_score: float = Field(alias="matchScore")
    location: str
    source: str
    posted_date: Optional[datetime] = Field(default=None, alias="postedDate")
    employment_type: Optional[str] = Field(default=None, alias="employmentType")
    salary_min: Optional[float] = Field(default=None, alias="salaryMin")
    salary_max: Optional[float] = Field(default=None, alias="salaryMax")
    currency: Optional[str] = "USD"
    apply_url: str = Field(alias="applyUrl")
    company_website: Optional[str] = Field(default=None, alias="companyWebsite")
    missing_skills: List[str] = Field(default_factory=list, alias="missingSkills")
    is_saved: bool = Field(default=False, alias="isSaved")


class DashboardTrends(BaseModel):
    """Historical snapshot delta indicators."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    match_score_delta: float = Field(default=0.0, alias="matchScoreDelta")
    jobs_matched_delta: int = Field(default=0, alias="jobsMatchedDelta")
    profile_score_delta: float = Field(default=0.0, alias="profileScoreDelta")
    readiness_delta: float = Field(default=0.0, alias="readinessDelta")


class DashboardOverviewResponse(BaseModel):
    """Full dashboard summary response for GET /api/v1/dashboard."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_jobs: int = Field(alias="totalJobs")
    jobs_matched: int = Field(alias="jobsMatched")
    average_match_score: float = Field(alias="averageMatchScore")
    excellent_matches: int = Field(alias="excellentMatches")
    strong_matches: int = Field(alias="strongMatches")
    moderate_matches: int = Field(alias="moderateMatches")
    weak_matches: int = Field(alias="weakMatches")

    trends: DashboardTrends = Field(default_factory=DashboardTrends)
    top_matches: List[MatchInsightItem] = Field(default_factory=list, alias="topMatches")

    profile_score: float = Field(alias="profileScore")
    readiness_score: float = Field(alias="readinessScore")

    latency_ms: float = Field(default=0.0, alias="latencyMs")
    generated_at: datetime = Field(alias="generatedAt")


class ProfileHealthBreakdown(BaseModel):
    """Component scores contributing to overall profile health."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    resume_completeness: float = Field(alias="resumeCompleteness")
    skill_coverage: float = Field(alias="skillCoverage")
    experience_coverage: float = Field(alias="experienceCoverage")
    education_coverage: float = Field(alias="educationCoverage")


class ProfileHealthResponse(BaseModel):
    """Profile health evaluation for GET /api/v1/dashboard/profile-health."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    overall_score: float = Field(alias="overallScore")
    breakdown: ProfileHealthBreakdown
    strengths: List[str] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list, alias="actionableRecommendations")
    last_updated: datetime = Field(alias="lastUpdated")


class CareerReadinessFactors(BaseModel):
    """Readiness sub-metric pillars."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    resume_quality: float = Field(alias="resumeQuality")
    skills_alignment: float = Field(alias="skillsAlignment")
    experience_depth: float = Field(alias="experienceDepth")
    market_match_rate: float = Field(alias="marketMatchRate")


class CareerReadinessResponse(BaseModel):
    """Career readiness score and explanation for GET /api/v1/dashboard/readiness."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    career_readiness_score: float = Field(alias="careerReadinessScore")
    tier: str
    factors: CareerReadinessFactors
    explanation: str
    key_competencies: List[str] = Field(default_factory=list, alias="keyCompetencies")
    growth_priorities: List[str] = Field(default_factory=list, alias="growthPriorities")
    generated_at: datetime = Field(alias="generatedAt")


class SkillFrequencyItem(BaseModel):
    """Frequency and status of a skill identified across matched opportunities."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    count: int
    percentage: float
    in_candidate_profile: bool = Field(default=False, alias="inCandidateProfile")
    priority: Optional[str] = None
    category: Optional[str] = None
    recommendation: Optional[str] = None


class SkillGapAnalysisResponse(BaseModel):
    """Skill gap analysis across matched jobs for GET /api/v1/dashboard/skills."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_analyzed_jobs: int = Field(alias="totalAnalyzedJobs")
    candidate_skills_count: int = Field(alias="candidateSkillsCount")
    most_requested_skills: List[SkillFrequencyItem] = Field(default_factory=list, alias="mostRequestedSkills")
    missing_skills: List[SkillFrequencyItem] = Field(default_factory=list, alias="missingSkills")
    emerging_skills: List[SkillFrequencyItem] = Field(default_factory=list, alias="emergingSkills")
    recommendations: List[str] = Field(default_factory=list)


class DistributionItem(BaseModel):
    """Generic category distribution slice for pie/donut and bar charts."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    value: int
    color: str
    percentage: float


class MatchDistributionData(BaseModel):
    """Breakdown of matches across tier categories."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    excellent: int
    strong: int
    moderate: int
    weak: int
    total: int
    items: List[DistributionItem] = Field(default_factory=list)


class TopSkillDemandItem(BaseModel):
    """Skill demand data point for charts."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    demand: int
    value_score: float = Field(alias="valueScore")


class MissingSkillItem(BaseModel):
    """Missing skill frequency for charts."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: str
    frequency: int
    importance: str


class LocationDistributionItem(BaseModel):
    """Location type proportion (Remote, Hybrid, Onsite)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    type: str
    count: int
    percentage: float


class AnalyticsSnapshotItem(BaseModel):
    """Single historical snapshot point for trend charts."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    timestamp: datetime
    profile_score: float = Field(alias="profileScore")
    readiness_score: float = Field(alias="readinessScore")
    average_match_score: float = Field(alias="averageMatchScore")
    excellent_matches: int = Field(alias="excellentMatches")
    strong_matches: int = Field(alias="strongMatches")
    moderate_matches: int = Field(alias="moderateMatches")
    weak_matches: int = Field(alias="weakMatches")


class AnalyticsDashboardResponse(BaseModel):
    """Full analytics dataset for GET /api/v1/dashboard/analytics."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    match_distribution: MatchDistributionData = Field(alias="matchDistribution")
    top_skills: List[TopSkillDemandItem] = Field(default_factory=list, alias="topSkills")
    missing_skills: List[MissingSkillItem] = Field(default_factory=list, alias="missingSkills")
    location_distribution: List[LocationDistributionItem] = Field(default_factory=list, alias="locationDistribution")
    profile_progress: List[AnalyticsSnapshotItem] = Field(default_factory=list, alias="profileProgress")
    latency_ms: float = Field(default=0.0, alias="latencyMs")
    generated_at: datetime = Field(alias="generatedAt")
