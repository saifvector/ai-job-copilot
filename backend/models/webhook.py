import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class WebhookModel(Base, UUIDPrimaryKeyMixin):
    """
    Webhook model stores endpoint subscription URLs, HMAC secrets, and event subscriptions.
    Table: webhooks
    """
    __tablename__ = "webhooks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(String(1024), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    events: Mapped[List[str]] = mapped_column(
        ARRAY(Text).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
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
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="webhooks")
    delivery_logs: Mapped[List["WebhookDeliveryLogModel"]] = relationship(
        "WebhookDeliveryLogModel",
        back_populates="webhook",
        cascade="all, delete-orphan",
        order_by="desc(WebhookDeliveryLogModel.created_at)",
    )

    def __repr__(self) -> str:
        return f"<WebhookModel id={self.id} endpoint={self.endpoint} enabled={self.enabled}>"


class WebhookDeliveryLogModel(Base, UUIDPrimaryKeyMixin):
    """
    WebhookDeliveryLog model captures delivery attempts, HTTP response codes, latency, and payloads.
    Table: webhook_delivery_logs
    """
    __tablename__ = "webhook_delivery_logs"

    webhook_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("webhooks.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    event: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    webhook: Mapped["WebhookModel"] = relationship("WebhookModel", back_populates="delivery_logs")

    def __repr__(self) -> str:
        return f"<WebhookDeliveryLogModel id={self.id} event={self.event} success={self.success}>"
