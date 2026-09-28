import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PublicProfileResponse(BaseModel):
    user_id: uuid.UUID
    name: str
    email: str
    phone: Optional[str] = None
    summary: Optional[str] = None
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    years_of_experience: int = 0
    skills: List[str] = []


class PublicResumeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    skills: List[str] = []


class PublicResumeListResponse(BaseModel):
    items: List[PublicResumeResponse]
    total: int


class PublicMatchResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    company: str
    location: str
    overall_score: float
    skill_score: float
    experience_score: float
    strengths: List[str] = []
    missing_skills: List[str] = []
    recommendations: List[str] = []
    apply_url: Optional[str] = None


class PublicMatchListResponse(BaseModel):
    items: List[PublicMatchResponse]
    total: int


class PublicApplicationCreateRequest(BaseModel):
    job_id: uuid.UUID = Field(..., description="Target Job ID")
    resume_id: Optional[uuid.UUID] = Field(None, description="Resume ID used for application")
    status: Optional[str] = Field(default="Applied", description="Initial status")
    notes: Optional[str] = Field(None, description="Candidate or API notes")


class PublicApplicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    job_title: Optional[str] = None
    company: Optional[str] = None
    status: str
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PublicApplicationListResponse(BaseModel):
    items: List[PublicApplicationResponse]
    total: int


class PublicReportResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    report_type: str
    format: str
    file_size_bytes: int
    created_at: datetime


class PublicReportListResponse(BaseModel):
    items: List[PublicReportResponse]
    total: int
