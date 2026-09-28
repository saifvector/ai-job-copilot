from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

InteractionType = Literal[
    "Message",
    "Email",
    "Referral",
    "Call",
    "Interview",
]

ReferralStatus = Literal[
    "Requested",
    "Received",
    "Declined",
    "Pending",
]


class ContactInteractionCreateRequest(BaseModel):
    """Payload to log a new interaction with a recruiter or contact."""
    interaction_type: InteractionType = Field(
        ...,
        alias="interactionType",
        description="Type of interaction: Message, Email, Referral, Call, Interview"
    )
    summary: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Detailed notes or overview of the interaction"
    )
    interaction_date: Optional[datetime] = Field(
        None,
        alias="interactionDate",
        description="Timestamp of the interaction; defaults to current time if omitted"
    )

    model_config = ConfigDict(populate_by_name=True)


class ContactInteractionResponse(BaseModel):
    """Interaction response item."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    recruiter_id: UUID = Field(..., serialization_alias="recruiterId")
    interaction_type: str = Field(..., serialization_alias="interactionType")
    summary: str
    interaction_date: datetime = Field(..., serialization_alias="interactionDate")
    created_at: datetime = Field(..., serialization_alias="createdAt")


class ReferralCreateRequest(BaseModel):
    """Payload to request or record a job referral."""
    company: str = Field(..., min_length=1, max_length=255, description="Company name")
    role: str = Field(..., min_length=1, max_length=255, description="Job title / role")
    status: ReferralStatus = Field("Requested", description="Status: Requested, Received, Declined, Pending")
    notes: Optional[str] = Field(None, max_length=5000, description="Notes, requisition ID, or referral links")

    model_config = ConfigDict(populate_by_name=True)


class ReferralUpdateRequest(BaseModel):
    """Payload to update referral status or details."""
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[ReferralStatus] = Field(None, description="Status: Requested, Received, Declined, Pending")
    notes: Optional[str] = Field(None, max_length=5000)

    model_config = ConfigDict(populate_by_name=True)


class ReferralResponse(BaseModel):
    """Referral details response."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    recruiter_id: UUID = Field(..., serialization_alias="recruiterId")
    company: str
    role: str
    status: str
    notes: Optional[str] = None
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")
    recruiter_name: Optional[str] = Field(None, serialization_alias="recruiterName")


class RecruiterCreateRequest(BaseModel):
    """Payload to add a new recruiter or networking contact."""
    name: str = Field(..., min_length=1, max_length=255, description="Full name of recruiter or contact")
    company: str = Field(..., min_length=1, max_length=255, description="Company or firm name")
    title: Optional[str] = Field(None, max_length=255, description="Job title (e.g. Senior Tech Recruiter)")
    email: Optional[str] = Field(None, max_length=255, description="Direct email address")
    linkedin_url: Optional[str] = Field(None, alias="linkedinUrl", max_length=500, description="LinkedIn profile URL")
    notes: Optional[str] = Field(None, max_length=10000, description="General contact notes")

    model_config = ConfigDict(populate_by_name=True)


class RecruiterUpdateRequest(BaseModel):
    """Payload to update an existing recruiter profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, alias="linkedinUrl", max_length=500)
    notes: Optional[str] = Field(None, max_length=10000)

    model_config = ConfigDict(populate_by_name=True)


class RecruiterResponse(BaseModel):
    """Recruiter summary response item."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    user_id: UUID = Field(..., serialization_alias="userId")
    name: str
    company: str
    title: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = Field(None, serialization_alias="linkedinUrl")
    notes: Optional[str] = None
    interaction_count: int = Field(0, serialization_alias="interactionCount")
    referral_count: int = Field(0, serialization_alias="referralCount")
    last_interaction_date: Optional[datetime] = Field(None, serialization_alias="lastInteractionDate")
    created_at: datetime = Field(..., serialization_alias="createdAt")
    updated_at: datetime = Field(..., serialization_alias="updatedAt")


class RecruiterDetailResponse(RecruiterResponse):
    """Detailed recruiter response with full interaction history and referrals."""
    interactions: List[ContactInteractionResponse] = Field(default_factory=list)
    referrals: List[ReferralResponse] = Field(default_factory=list)


class RecruiterListResponse(BaseModel):
    """List response for recruiters."""
    model_config = ConfigDict(populate_by_name=True)

    recruiters: List[RecruiterResponse]
    total: int
    companies: List[str] = Field(default_factory=list)


class NetworkingAnalyticsResponse(BaseModel):
    """Networking and outreach intelligence analytics."""
    model_config = ConfigDict(populate_by_name=True)

    recruiters_contacted: int = Field(..., serialization_alias="recruitersContacted")
    response_rate: float = Field(..., serialization_alias="responseRate")
    referral_success_rate: float = Field(..., serialization_alias="referralSuccessRate")
    companies_reached: int = Field(..., serialization_alias="companiesReached")
    messages_sent: int = Field(..., serialization_alias="messagesSent")
    responses_received: int = Field(..., serialization_alias="responsesReceived")
    referrals_requested: int = Field(..., serialization_alias="referralsRequested")
    referrals_received: int = Field(..., serialization_alias="referralsReceived")
    interactions_by_type: Dict[str, int] = Field(default_factory=dict, serialization_alias="interactionsByType")
    referrals_by_status: Dict[str, int] = Field(default_factory=dict, serialization_alias="referralsByStatus")
