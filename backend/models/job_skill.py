import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.job import JobModel


class JobSkillModel(Base, UUIDPrimaryKeyMixin):
    """
    JobSkill model representing technical or domain skills extracted from a job posting.
    Table: job_skills (Prisma mapped)
    """
    __tablename__ = "job_skills"

    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to JobModel
    job: Mapped["JobModel"] = relationship(
        "JobModel",
        back_populates="skills",
        lazy="select",
    )

    __table_args__ = (
        Index("idx_job_skills_job_id", "job_id"),
        Index("idx_job_skills_skill_name", "skill_name"),
    )

    def __repr__(self) -> str:
        return f"<JobSkillModel id={self.id} job_id={self.job_id} skill_name='{self.skill_name}'>"
