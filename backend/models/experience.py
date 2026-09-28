import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class ExperienceModel(Base, UUIDPrimaryKeyMixin):
    """
    Experience model representing employment roles and accomplishments.
    Table: experience (Prisma mapped)
    """
    __tablename__ = "experience"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to User
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="experience",
        lazy="select",
    )


    __table_args__ = (
        Index("idx_experience_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ExperienceModel id={self.id} user_id={self.user_id} company='{self.company}' role='{self.role}'>"
