import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.application import ApplicationModel


class ApplicationEventModel(Base, UUIDPrimaryKeyMixin):
    """
    ApplicationEvent model capturing chronological history and status changes.
    Table: application_events (Prisma mapped)
    """
    __tablename__ = "application_events"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    application: Mapped["ApplicationModel"] = relationship(
        "ApplicationModel",
        back_populates="events",
    )

    __table_args__ = (
        Index("idx_application_events_application_id", "application_id"),
        Index("idx_application_events_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<ApplicationEventModel id={self.id} app_id={self.application_id} type='{self.event_type}'>"
