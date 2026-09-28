import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class EducationBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    institution: str = Field(..., min_length=1, max_length=255, example="University of California, Berkeley")
    degree: str = Field(..., min_length=1, max_length=255, example="Bachelor of Science")
    field_of_study: Optional[str] = Field(default=None, max_length=255, example="Computer Science")
    start_date: Optional[str] = Field(default=None, max_length=50, example="2020")
    end_date: Optional[str] = Field(default=None, max_length=50, example="2024")


class EducationCreate(EducationBase):
    user_id: uuid.UUID


class EducationResponse(EducationBase):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
