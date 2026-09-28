import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class OAuthConnectionModel(Base, UUIDPrimaryKeyMixin):
    """
    OAuthConnection model stores OAuth tokens, provider identities, and metadata for external integrations
    (Gmail, Outlook, Google Calendar, Outlook Calendar, Google Drive, Dropbox, OneDrive, Slack).
    Table: oauth_connections
    """
    __tablename__ = "oauth_connections"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    scopes: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )
    metadata_json: Mapped[Optional[str]] = mapped_column("metadata", Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="connected", nullable=False, index=True)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_oauth_connections_user_provider"),
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="oauth_connections")

    def __repr__(self) -> str:
        return f"<OAuthConnectionModel id={self.id} provider={self.provider} status={self.status}>"
