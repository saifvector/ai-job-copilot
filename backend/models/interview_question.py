import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.interview_preparation import InterviewPreparationModel


class QuestionModel(Base, UUIDPrimaryKeyMixin):
    """
    Question database model storing categorized interview questions, sample answers,
    explanations, and candidate practice evaluations.
    Table: interview_questions (Prisma mapped)
    """
    __tablename__ = "interview_questions"

    preparation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("interview_preparations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    sample_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    user_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(
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
    preparation: Mapped["InterviewPreparationModel"] = relationship(
        "InterviewPreparationModel",
        back_populates="questions",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_questions_preparation_id", "preparation_id"),
        Index("idx_questions_category", "category"),
        Index("idx_questions_difficulty", "difficulty"),
        Index("idx_questions_is_completed", "is_completed"),
    )

    def __repr__(self) -> str:
        return f"<QuestionModel id={self.id} category='{self.category}' difficulty='{self.difficulty}' completed={self.is_completed}>"
