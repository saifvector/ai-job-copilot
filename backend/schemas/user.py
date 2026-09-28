import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from schemas.profile import ProfileRead


class UserBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Full name of user",
        example="Alex Chen",
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address",
        example="alex.chen@example.com",
    )


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserWithProfileRead(UserRead):
    profile: Optional[ProfileRead] = None
