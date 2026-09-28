import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, Float, ForeignKey, Index, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.job import JobModel
    from models.user import UserModel


class MatchResultModel(Base, UUIDPrimaryKeyMixin):
    """
    MatchResult model storing job fit scores and AI gap analysis for candidates.
    Table: match_results (Prisma mapped)
    """
    __tablename__ = "match_results"

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

    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    skill_score: Mapped[float] = mapped_column(Float, nullable=False)
    experience_score: Mapped[float] = mapped_column(Float, nullable=False)
    education_score: Mapped[float] = mapped_column(Float, nullable=False)
    location_score: Mapped[float] = mapped_column(Float, nullable=False)
    role_score: Mapped[float] = mapped_column(Float, nullable=False)

    strengths: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )
    missing_skills: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )
    recommendations: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )

    generated_at: Mapped[datetime] = mapped_column(
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
        back_populates="match_results",
    )
    job: Mapped["JobModel"] = relationship(
        "JobModel",
        back_populates="match_results",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_match_results_user_job"),
        Index("idx_match_results_user_score", "user_id", "overall_score"),
    )
