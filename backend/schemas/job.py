from datetime import datetime
from typing import List, Optional, Dict
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class JobSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    skill_name: str = Field(..., alias="skillName")
    created_at: datetime = Field(..., alias="createdAt")


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    source: str
    external_id: str = Field(..., alias="externalId")
    title: str
    company: str
    location: str
    employment_type: Optional[str] = Field(None, alias="employmentType")
    salary_min: Optional[float] = Field(None, alias="salaryMin")
    salary_max: Optional[float] = Field(None, alias="salaryMax")
    currency: Optional[str] = "USD"
    description: str
    requirements: Optional[str] = None
    apply_url: str = Field(..., alias="applyUrl")
    company_website: Optional[str] = Field(None, alias="companyWebsite")
    posted_at: Optional[datetime] = Field(None, alias="postedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    skills: List[str] = Field(default_factory=list)


class JobListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    items: List[JobResponse]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    total_pages: int = Field(..., alias="totalPages")


class JobFilterParams(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    query: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    skill: Optional[str] = None
    min_salary: Optional[float] = Field(None, alias="minSalary")
    sort_by: str = Field("newest", alias="sortBy")  # 'newest', 'highest_salary', 'most_relevant'
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100, alias="pageSize")


class JobSyncRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    source: Optional[str] = None
    limit_per_source: int = Field(50, ge=1, le=200, alias="limitPerSource")


class JobSyncResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    synced_count: int = Field(..., alias="syncedCount")
    duplicates_skipped: int = Field(..., alias="duplicatesSkipped")
    errors_count: int = Field(0, alias="errorsCount")
    sources: Dict[str, int] = Field(default_factory=dict)
    duration_ms: float = Field(..., alias="durationMs")
    message: str

