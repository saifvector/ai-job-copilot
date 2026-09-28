import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class CareerIntelligenceSnapshotModel(Base, UUIDPrimaryKeyMixin):
    """
    CareerIntelligenceSnapshotModel persists historical analytical rollups, cohort snapshots,
    and data warehouse records for longitudinal career intelligence and trend analysis.
    Table: career_intelligence_snapshots
    """
    __tablename__ = "career_intelligence_snapshots"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    total_applications: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interview_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    offer_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rejection_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_response_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metrics_payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="career_intelligence_snapshots")

    __table_args__ = (
        Index("idx_career_snapshots_user_id", "user_id"),
        Index("idx_career_snapshots_date", "snapshot_date"),
    )

    def __repr__(self) -> str:
        return f"<CareerIntelligenceSnapshotModel id={self.id} date={self.snapshot_date} apps={self.total_applications}>"
