import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CertificationBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=255, example="AWS Certified Solutions Architect - Associate")
    issuer: str = Field(..., min_length=1, max_length=255, example="Amazon Web Services")
    issue_date: Optional[str] = Field(default=None, max_length=50, example="2023")


class CertificationCreate(CertificationBase):
    user_id: uuid.UUID


class CertificationResponse(CertificationBase):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
