import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import DateTime, Float, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.job_skill import JobSkillModel
    from models.match_result import MatchResultModel
    from models.tailored_resume import TailoredResumeModel
    from models.application import ApplicationModel
    from models.interview_preparation import InterviewPreparationModel
    from models.application_draft import ApplicationDraftModel



class JobModel(Base, UUIDPrimaryKeyMixin):
    """
    Job model representing aggregated job postings from external job boards and APIs.
    Table: jobs (Prisma mapped)
    """
    __tablename__ = "jobs"

    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="USD")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    apply_url: Mapped[str] = mapped_column(Text, nullable=False)
    company_website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
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

    # 1-to-many relationship with JobSkillModel
    skills: Mapped[List["JobSkillModel"]] = relationship(
        "JobSkillModel",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-many relationship with MatchResultModel
    match_results: Mapped[List["MatchResultModel"]] = relationship(
        "MatchResultModel",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-many relationship with TailoredResumeModel
    tailored_resumes: Mapped[List["TailoredResumeModel"]] = relationship(
        "TailoredResumeModel",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-many relationship with ApplicationModel
    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-many relationship with InterviewPreparationModel
    interview_preparations: Mapped[List["InterviewPreparationModel"]] = relationship(
        "InterviewPreparationModel",
        back_populates="job",
        lazy="selectin",
    )

    # 1-to-many relationship with ApplicationDraftModel
    application_drafts: Mapped[List["ApplicationDraftModel"]] = relationship(
        "ApplicationDraftModel",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_jobs_source_external_id"),
        Index("idx_jobs_company_title", "company", "title"),
        Index("idx_jobs_location", "location"),
        Index("idx_jobs_source", "source"),
        Index("idx_jobs_posted_at", "posted_at"),
    )

    def __repr__(self) -> str:
        return f"<JobModel id={self.id} source='{self.source}' company='{self.company}' title='{self.title}'>"
