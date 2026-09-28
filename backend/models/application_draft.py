import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.application_question import ApplicationQuestionModel
    from models.job import JobModel
    from models.user import UserModel


class ApplicationDraftModel(Base, UUIDPrimaryKeyMixin):
    """
    ApplicationDraft model tracks pre-submission job application preparation,
    selected resumes, checklist readiness, and AI-generated answers.
    Table: application_drafts (Prisma mapped)
    """
    __tablename__ = "application_drafts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Draft",
        index=True,
    )
    generated_answers: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    selected_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
    )
    readiness_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    checklist: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="application_drafts",
    )
    job: Mapped["JobModel"] = relationship(
        "JobModel",
        back_populates="application_drafts",
    )
    questions: Mapped[List["ApplicationQuestionModel"]] = relationship(
        "ApplicationQuestionModel",
        back_populates="draft",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ApplicationQuestionModel.order",
    )

    __table_args__ = (
        Index("idx_application_drafts_user_id", "user_id"),
        Index("idx_application_drafts_job_id", "job_id"),
        Index("idx_application_drafts_status", "status"),
    )
