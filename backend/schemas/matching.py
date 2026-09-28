"""
Pydantic Schemas for Phase 5 AI Job Matching Engine API.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MatchJobSnippet(BaseModel):
    """Joined job listing metadata for match cards and detail views."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    title: str
    company: str
    location: str
    employment_type: Optional[str] = Field(default=None, alias="employmentType")
    salary_min: Optional[float] = Field(default=None, alias="salaryMin")
    salary_max: Optional[float] = Field(default=None, alias="salaryMax")
    currency: Optional[str] = "USD"
    source: str
    apply_url: str = Field(alias="applyUrl")
    company_website: Optional[str] = Field(default=None, alias="companyWebsite")
    posted_at: Optional[datetime] = Field(default=None, alias="postedAt")
    description: Optional[str] = None
    requirements: Optional[str] = None


class MatchResultResponse(BaseModel):
    """Detailed candidate-to-job matching evaluation."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID = Field(alias="userId")
    job_id: uuid.UUID = Field(alias="jobId")

    overall_score: float = Field(alias="overallScore")
    skill_score: float = Field(alias="skillScore")
    experience_score: float = Field(alias="experienceScore")
    education_score: float = Field(alias="educationScore")
    location_score: float = Field(alias="locationScore")
    role_score: float = Field(alias="roleScore")

    strengths: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list, alias="missingSkills")
    recommendations: List[str] = Field(default_factory=list)

    generated_at: datetime = Field(alias="generatedAt")
    updated_at: datetime = Field(alias="updatedAt")

    job: Optional[MatchJobSnippet] = None


class MatchRunRequest(BaseModel):
    """Request payload to initiate candidate matching against job listings."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    job_ids: Optional[List[uuid.UUID]] = Field(default=None, alias="jobIds")
    limit: int = Field(default=500, ge=1, le=2000)


class MatchRunResponse(BaseModel):
    """Summary of batch matching execution."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_evaluated: int = Field(alias="totalEvaluated")
    matches_saved: int = Field(alias="matchesSaved")
    top_score: float = Field(alias="topScore")
    duration_ms: float = Field(alias="durationMs")
