import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.recruiter import RecruiterModel


class ContactInteractionModel(Base, UUIDPrimaryKeyMixin):
    """
    ContactInteraction database model capturing chronological outreach, messages, calls, and meetings.
    Table: contact_interactions (Prisma mapped)
    """
    __tablename__ = "contact_interactions"

    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    # Types: Message, Email, Referral, Call, Interview
    interaction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    interaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    recruiter: Mapped["RecruiterModel"] = relationship(
        "RecruiterModel",
        back_populates="interactions",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_contact_interactions_recruiter_id", "recruiter_id"),
        Index("idx_contact_interactions_date", "interaction_date"),
        Index("idx_contact_interactions_type", "interaction_type"),
    )

    def __repr__(self) -> str:
        return f"<ContactInteractionModel id={self.id} type='{self.interaction_type}' date={self.interaction_date}>"
