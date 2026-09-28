import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.application_event import ApplicationEventModel
    from models.interview import InterviewModel
    from models.job import JobModel
    from models.tailored_resume import TailoredResumeModel
    from models.user import UserModel
    from models.outcome_event import OutcomeEventModel


class ApplicationModel(Base, UUIDPrimaryKeyMixin):
    """
    Application model representing a job application in the candidate's tracking pipeline.
    Table: applications (Prisma mapped)
    """
    __tablename__ = "applications"

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
    tailored_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tailored_resumes.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )

    # Statuses: SAVED, APPLIED, ASSESSMENT, INTERVIEW, OFFER, REJECTED, WITHDRAWN
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SAVED",
        index=True,
    )
    application_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="applications",
        lazy="selectin",
    )
    job: Mapped["JobModel"] = relationship(
        "JobModel",
        back_populates="applications",
        lazy="selectin",
    )
    tailored_resume: Mapped[Optional["TailoredResumeModel"]] = relationship(
        "TailoredResumeModel",
        back_populates="applications",
        lazy="selectin",
    )
    events: Mapped[List["ApplicationEventModel"]] = relationship(
        "ApplicationEventModel",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationEventModel.created_at.desc()",
        lazy="selectin",
    )
    interviews: Mapped[List["InterviewModel"]] = relationship(
        "InterviewModel",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="InterviewModel.interview_date.asc()",
        lazy="selectin",
    )
    outcome_events: Mapped[List["OutcomeEventModel"]] = relationship(
        "OutcomeEventModel",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="OutcomeEventModel.occurred_at.desc()",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),
        Index("idx_applications_user_id", "user_id"),
        Index("idx_applications_job_id", "job_id"),
        Index("idx_applications_status", "status"),
        Index("idx_applications_user_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<ApplicationModel id={self.id} user_id={self.user_id} job_id={self.job_id} status='{self.status}'>"
