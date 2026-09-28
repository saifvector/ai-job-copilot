from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

ApplicationStatus = Literal[
    "SAVED",
    "APPLIED",
    "ASSESSMENT",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]

InterviewType = Literal[
    "HR",
    "TECHNICAL",
    "MANAGERIAL",
    "FINAL",
]


class InterviewCreateRequest(BaseModel):
    """Payload to schedule an interview round."""
    interview_type: InterviewType = Field(
        ...,
        description="Type of interview: HR, TECHNICAL, MANAGERIAL, FINAL"
    )
    interview_date: datetime = Field(
        ...,
        description="Scheduled ISO datetime of the interview"
    )
    interview_round: int = Field(
        1,
        ge=1,
        description="Interview round number (1, 2, 3...)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Preparation notes or interviewer details"
    )


class InterviewResponse(BaseModel):
    """Interview round response object."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    interview_type: str
    interview_date: datetime
    interview_round: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ApplicationEventCreateRequest(BaseModel):
    """Payload to record an application event or milestone."""
    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Event type identifier, e.g. STATUS_CHANGE, NOTE_ADDED, INTERVIEW_SCHEDULED"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Chronological event narrative description"
    )


class ApplicationEventResponse(BaseModel):
    """Application event response object."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    event_type: str
    description: str
    created_at: datetime


class ApplicationJobSummary(BaseModel):
    """Target job summary attached to application."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    company: str
    location: str
    employment_type: Optional[str] = None
    apply_url: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "USD"


class ApplicationCreateRequest(BaseModel):
    """Payload to create or track a new job application."""
    job_id: UUID = Field(..., description="Target Job UUID")
    status: ApplicationStatus = Field("SAVED", description="Initial pipeline status")
    tailored_resume_id: Optional[UUID] = Field(None, description="Optional tailored resume UUID used")
    application_date: Optional[datetime] = Field(None, description="Date submitted if already applied")
    source: Optional[str] = Field(None, max_length=100, description="Source or job board name")
    notes: Optional[str] = Field(None, max_length=5000, description="Personal application notes")


class ApplicationStatusUpdateRequest(BaseModel):
    """Payload to transition application pipeline status."""
    status: ApplicationStatus = Field(..., description="New pipeline status")
    notes: Optional[str] = Field(None, max_length=5000, description="Optional transition note or rationale")


class ApplicationNotesUpdateRequest(BaseModel):
    """Payload to update candidate notes on an application."""
    notes: str = Field(..., max_length=10000, description="Updated notes content")


class ApplicationListItem(BaseModel):
    """Summary representation for pipeline kanban cards and list views."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    job_id: UUID
    job_title: str
    job_company: str
    job_location: str
    status: str
    application_date: Optional[datetime] = None
    last_updated: datetime
    source: Optional[str] = None
    notes: Optional[str] = None
    interview_count: int = 0
    next_interview_date: Optional[datetime] = None
    tailored_resume_id: Optional[UUID] = None


class ApplicationResponse(BaseModel):
    """Complete application entity with nested job, events, and interviews."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    job_id: UUID
    tailored_resume_id: Optional[UUID] = None
    status: str
    application_date: Optional[datetime] = None
    last_updated: datetime
    source: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    job: Optional[ApplicationJobSummary] = None
    events: List[ApplicationEventResponse] = []
    interviews: List[InterviewResponse] = []


class PipelineResponse(BaseModel):
    """Grouped pipeline for Kanban board view."""
    saved: List[ApplicationListItem] = []
    applied: List[ApplicationListItem] = []
    assessment: List[ApplicationListItem] = []
    interview: List[ApplicationListItem] = []
    offer: List[ApplicationListItem] = []
    rejected: List[ApplicationListItem] = []
    withdrawn: List[ApplicationListItem] = []
    total_active: int = 0
    total_applications: int = 0


class ApplicationAnalyticsResponse(BaseModel):
    """Application pipeline metrics and conversion performance."""
    total_applications: int
    applications_sent: int
    interviews_received: int
    offers_received: int
    rejections: int
    response_rate: float
    interview_rate: float
    offer_rate: float
    by_status: Dict[str, int]
    by_source: Dict[str, int]
    interviews_scheduled_upcoming: int
    applications_this_month: int
