import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.job import JobModel
    from models.resume import ResumeModel
    from models.user import UserModel
    from models.application import ApplicationModel
    from models.resume_performance import ResumePerformanceModel


class TailoredResumeModel(Base, UUIDPrimaryKeyMixin):
    """
    TailoredResume model tracking tailored resume variations customized for specific target jobs.
    Table: tailored_resumes (Prisma mapped)
    """
    __tablename__ = "tailored_resumes"

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
    original_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded payload containing all sections & versions
    ats_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    keyword_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

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
        back_populates="tailored_resumes",
        lazy="selectin",
    )
    job: Mapped["JobModel"] = relationship(
        "JobModel",
        back_populates="tailored_resumes",
        lazy="selectin",
    )
    original_resume: Mapped[Optional["ResumeModel"]] = relationship(
        "ResumeModel",
        lazy="selectin",
    )
    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel",
        back_populates="tailored_resume",
        lazy="selectin",
    )
    resume_performances: Mapped[List["ResumePerformanceModel"]] = relationship(
        "ResumePerformanceModel",
        back_populates="tailored_resume",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_tailored_resumes_user_id", "user_id"),
        Index("idx_tailored_resumes_job_id", "job_id"),
        Index("idx_tailored_resumes_user_job", "user_id", "job_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<TailoredResumeModel id={self.id} user_id={self.user_id} "
            f"job_id={self.job_id} ats_score={self.ats_score}>"
        )
