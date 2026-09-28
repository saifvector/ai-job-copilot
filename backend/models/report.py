import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class ReportModel(Base, UUIDPrimaryKeyMixin):
    """
    Report database model representing generated document exports.
    Table: reports (Prisma mapped)
    """
    __tablename__ = "reports"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    # Types: APPLICATION_REPORT, MATCH_REPORT, SKILL_REPORT, CAREER_REPORT, RESUME_REPORT
    report_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    # Formats: PDF, CSV, XLSX, JSON
    format: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    download_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    generation_duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    generated_at: Mapped[datetime] = mapped_column(
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

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="reports",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_reports_user_id", "user_id"),
        Index("idx_reports_report_type", "report_type"),
        Index("idx_reports_generated_at", "generated_at"),
    )
