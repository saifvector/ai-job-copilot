import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.interview_question import QuestionModel
    from models.job import JobModel
    from models.user import UserModel


class InterviewPreparationModel(Base, UUIDPrimaryKeyMixin):
    """
    InterviewPreparation model tracks personalized interview question sets generated for roles and jobs.
    Table: interview_preparations (Prisma mapped)
    """
    __tablename__ = "interview_preparations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    preparation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Comprehensive",
        index=True,
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
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
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="interview_preparations",
    )
    job: Mapped[Optional["JobModel"]] = relationship(
        "JobModel",
        back_populates="interview_preparations",
    )
    questions: Mapped[List["QuestionModel"]] = relationship(
        "QuestionModel",
        back_populates="preparation",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="QuestionModel.created_at",
    )

    __table_args__ = (
        Index("idx_interview_preparations_user_id", "user_id"),
        Index("idx_interview_preparations_job_id", "job_id"),
        Index("idx_interview_preparations_role", "role"),
        Index("idx_interview_preparations_type", "preparation_type"),
    )

    def __repr__(self) -> str:
        return f"<InterviewPreparationModel id={self.id} role='{self.role}' type='{self.preparation_type}'>"
