import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class AnalyticsSnapshotModel(Base, UUIDPrimaryKeyMixin):
    """
    AnalyticsSnapshot model tracking historical dashboard metrics and profile progress for trend analysis.
    Table: analytics_snapshots (Prisma mapped)
    """
    __tablename__ = "analytics_snapshots"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    profile_score: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_score: Mapped[float] = mapped_column(Float, nullable=False)
    average_match_score: Mapped[float] = mapped_column(Float, nullable=False)

    excellent_matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    strong_matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    moderate_matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    weak_matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="analytics_snapshots",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_analytics_snapshots_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AnalyticsSnapshotModel id={self.id} user_id={self.user_id} "
            f"profile_score={self.profile_score} readiness_score={self.readiness_score}>"
        )
