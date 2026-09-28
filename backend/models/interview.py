import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.application import ApplicationModel


class InterviewModel(Base, UUIDPrimaryKeyMixin):
    """
    Interview model tracking scheduled and completed interview rounds.
    Table: interviews (Prisma mapped)
    """
    __tablename__ = "interviews"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    # Types: HR, Technical, Managerial, Final
    interview_type: Mapped[str] = mapped_column(String(50), nullable=False)
    interview_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    interview_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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

    # Relationship
    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel",
        back_populates="interviews",
    )

    __table_args__ = (
        Index("idx_interviews_application_id", "application_id"),
        Index("idx_interviews_interview_date", "interview_date"),
    )

    def __repr__(self) -> str:
        return f"<InterviewModel id={self.id} app_id={self.application_id} type='{self.interview_type}' round={self.interview_round}>"
