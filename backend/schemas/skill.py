import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

SKILL_CATEGORIES = [
    "Programming Language",
    "Framework",
    "Database",
    "Cloud",
    "AI/ML",
    "Tool",
    "Other",
]

SkillCategoryType = Literal[
    "Programming Language",
    "Framework",
    "Database",
    "Cloud",
    "AI/ML",
    "Tool",
    "Other",
]


class SkillBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=100, example="Python")
    category: str = Field(default="Other", max_length=50, example="Programming Language")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, example=0.95)


class SkillCreate(SkillBase):
    user_id: uuid.UUID


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
