import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ProjectBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str = Field(..., min_length=1, max_length=255, example="Autonomous AI Agent Platform")
    description: str = Field(default="", example="Engineered multi-agent orchestration pipeline using FastAPI and Gemini.")
    technologies: List[str] = Field(default_factory=list, example=["Python", "FastAPI", "PostgreSQL", "Docker"])


class ProjectCreate(ProjectBase):
    user_id: uuid.UUID


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
