import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.application_draft import ApplicationDraftModel


class ApplicationQuestionModel(Base, UUIDPrimaryKeyMixin):
    """
    ApplicationQuestion model stores questions for a job application draft,
    including answer types, AI-generated answers, and candidate edits.
    Table: application_questions (Prisma mapped)
    """
    __tablename__ = "application_questions"

    draft_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("application_drafts.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    generated_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    user_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    answer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Text",
        index=True,
    )
    options: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default="[]",
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_reviewed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
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
    draft: Mapped["ApplicationDraftModel"] = relationship(
        "ApplicationDraftModel",
        back_populates="questions",
    )

    __table_args__ = (
        Index("idx_application_questions_draft_id", "draft_id"),
        Index("idx_application_questions_type", "answer_type"),
    )
