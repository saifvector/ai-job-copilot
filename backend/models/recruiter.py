import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.contact_interaction import ContactInteractionModel
    from models.referral import ReferralModel
    from models.user import UserModel


class RecruiterModel(Base, UUIDPrimaryKeyMixin):
    """
    Recruiter database model representing professional contacts, hiring managers, and recruiters.
    Table: recruiters (Prisma mapped)
    """
    __tablename__ = "recruiters"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
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

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="recruiters",
    )
    referrals: Mapped[List["ReferralModel"]] = relationship(
        "ReferralModel",
        back_populates="recruiter",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ReferralModel.created_at)",
    )
    interactions: Mapped[List["ContactInteractionModel"]] = relationship(
        "ContactInteractionModel",
        back_populates="recruiter",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ContactInteractionModel.interaction_date)",
    )

    __table_args__ = (
        Index("idx_recruiters_user_id", "user_id"),
        Index("idx_recruiters_company", "company"),
        Index("idx_recruiters_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<RecruiterModel id={self.id} name='{self.name}' company='{self.company}'>"
