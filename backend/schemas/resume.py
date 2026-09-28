import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ResumeBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    original_filename: str = Field(
        ...,
        description="Original name of the uploaded document",
        example="Alex_Chen_Staff_Engineer_Resume.pdf",
    )
    file_type: str = Field(
        ...,
        description="MIME content type (PDF or DOCX)",
        example="application/pdf",
    )
    file_size: int = Field(
        ...,
        ge=1,
        description="File size in bytes",
        example=145820,
    )


class ResumeCreate(ResumeBase):
    user_id: uuid.UUID
    stored_filename: str
    file_path: str


class ResumeUpdate(BaseModel):
    original_filename: Optional[str] = None
    stored_filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    file_path: Optional[str] = None


class ResumeResponse(ResumeBase):
    """
    Public resume metadata representation.
    Never exposes internal filesystem paths to clients.
    """
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: uuid.UUID
    user_id: uuid.UUID
    uploaded_at: datetime
    updated_at: datetime
    download_url: str = Field(
        default="/api/v1/resume/download",
        description="Safe API endpoint for downloading the document",
    )


class ResumeDeleteResponse(BaseModel):
    success: bool = True
    message: str = "Resume successfully deleted."
