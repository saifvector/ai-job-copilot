import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.recruiter import RecruiterModel


class ReferralModel(Base, UUIDPrimaryKeyMixin):
    """
    Referral database model tracking internal job referrals.
    Table: referrals (Prisma mapped)
    """
    __tablename__ = "referrals"

    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    # Statuses: Requested, Received, Declined, Pending
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Requested",
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
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

    # Relationship
    recruiter: Mapped["RecruiterModel"] = relationship(
        "RecruiterModel",
        back_populates="referrals",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_referrals_recruiter_id", "recruiter_id"),
        Index("idx_referrals_status", "status"),
        Index("idx_referrals_company", "company"),
    )

    def __repr__(self) -> str:
        return f"<ReferralModel id={self.id} company='{self.company}' role='{self.role}' status='{self.status}'>"
