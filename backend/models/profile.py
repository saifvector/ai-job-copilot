import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text, Index, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class ProfileModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Profile database model representing candidate job search preferences.
    Table: profiles (Prisma mapped)
    """
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Compatible with PostgreSQL ARRAY and fallback JSON
    preferred_roles: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )

    preferred_locations: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )

    years_of_experience: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    resume_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship back to UserModel
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile",
        lazy="joined",
    )

    __table_args__ = (
        Index("idx_profiles_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ProfileModel id={self.id} user_id={self.user_id}>"
