import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ExperienceBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    company: str = Field(..., min_length=1, max_length=255, example="Google")
    role: str = Field(..., min_length=1, max_length=255, example="Senior Software Engineer")
    description: str = Field(default="", example="Architected high-throughput async APIs and distributed services.")
    start_date: Optional[str] = Field(default=None, max_length=50, example="Jan 2022")
    end_date: Optional[str] = Field(default=None, max_length=50, example="Present")


class ExperienceCreate(ExperienceBase):
    user_id: uuid.UUID


class ExperienceResponse(ExperienceBase):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
