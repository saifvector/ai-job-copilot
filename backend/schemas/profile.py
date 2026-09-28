import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    preferred_roles: List[str] = Field(
        default_factory=list,
        description="Target job titles / roles (e.g. ['Software Engineer', 'Architect'])",
        example=["Staff Software Engineer", "Backend Lead"],
    )
    preferred_locations: List[str] = Field(
        default_factory=list,
        description="Preferred job locations or 'Remote'",
        example=["Remote", "San Francisco, CA"],
    )
    years_of_experience: int = Field(
        default=0,
        ge=0,
        le=50,
        description="Total professional years of experience",
        example=6,
    )
    resume_url: Optional[str] = Field(
        default=None,
        description="Secure URI or cloud storage link to candidate resume",
        example="https://storage.jobcopilot.dev/resumes/candidate.pdf",
    )


class ProfileCreate(ProfileBase):
    user_id: uuid.UUID = Field(
        description="Associated user's UUID",
    )


class ProfileUpdate(BaseModel):
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    years_of_experience: Optional[int] = Field(default=None, ge=0, le=50)
    resume_url: Optional[str] = None


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
