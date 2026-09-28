import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel
    from models.tailored_resume import TailoredResumeModel


class ResumePerformanceModel(Base, UUIDPrimaryKeyMixin):
    """
    ResumePerformanceModel tracks empirical performance metrics for tailored resume versions.
    Measures applications sent, interviews received, offers received, and empirical response rate.
    Table: resume_performances
    """
    __tablename__ = "resume_performances"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    tailored_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tailored_resumes.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    applications_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interviews_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    offers_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
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
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="resume_performances")
    tailored_resume: Mapped[Optional["TailoredResumeModel"]] = relationship(
        "TailoredResumeModel",
        back_populates="resume_performances",
    )

    __table_args__ = (
        Index("idx_resume_performances_user_id", "user_id"),
        Index("idx_resume_performances_resume_id", "tailored_resume_id"),
        Index("idx_resume_performances_response_rate", "response_rate"),
    )

    def __repr__(self) -> str:
        return f"<ResumePerformanceModel id={self.id} resume_id={self.tailored_resume_id} rate={self.response_rate:.2f}>"
