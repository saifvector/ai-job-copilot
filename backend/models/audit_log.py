import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class AuditLogModel(Base, UUIDPrimaryKeyMixin):
    """
    AuditLog model captures forensic and compliance event records for critical actions:
    resume uploads, profile updates, report generation, application status transitions,
    authentication security events, and administrative actions.
    Table: audit_logs
    """
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        back_populates="audit_logs",
    )

    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_resource", "resource"),
        Index("idx_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLogModel id={self.id} action={self.action} resource={self.resource}>"
