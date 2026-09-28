import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class ApiKeyModel(Base, UUIDPrimaryKeyMixin):
    """
    ApiKey model stores hashed credentials for third-party developer API access.
    Table: api_keys
    """
    __tablename__ = "api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    prefix: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    scopes: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=lambda: ["read:profile", "read:resume", "read:matches", "read:applications", "read:reports"],
    )
    rate_limit: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    monthly_limit: Mapped[int] = mapped_column(Integer, default=10000, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
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
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<ApiKeyModel id={self.id} prefix={self.prefix} name={self.name} is_active={self.is_active}>"
