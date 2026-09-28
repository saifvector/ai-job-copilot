import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel
    from models.application import ApplicationModel


class OutcomeEventModel(Base, UUIDPrimaryKeyMixin):
    """
    OutcomeEventModel records critical milestone events in an application lifecycle.
    Outcome types: InterviewReceived, AssessmentReceived, OfferReceived, Rejected, Withdrawn.
    Table: outcome_events
    """
    __tablename__ = "outcome_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    outcome_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_payload: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="outcome_events")
    application: Mapped["ApplicationModel"] = relationship("ApplicationModel", back_populates="outcome_events")

    __table_args__ = (
        Index("idx_outcome_events_user_id", "user_id"),
        Index("idx_outcome_events_application_id", "application_id"),
        Index("idx_outcome_events_type", "outcome_type"),
        Index("idx_outcome_events_occurred_at", "occurred_at"),
    )

    def __repr__(self) -> str:
        return f"<OutcomeEventModel id={self.id} type={self.outcome_type} app_id={self.application_id}>"
