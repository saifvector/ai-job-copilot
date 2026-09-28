import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class MockInterviewModel(Base, UUIDPrimaryKeyMixin):
    """
    MockInterview database model recording candidate mock practice sessions,
    overall evaluation score, and structured AI feedback.
    Table: mock_interviews (Prisma mapped)
    """
    __tablename__ = "mock_interviews"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
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

    # Relationship
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="mock_interviews",
    )

    __table_args__ = (
        Index("idx_mock_interviews_user_id", "user_id"),
        Index("idx_mock_interviews_role", "role"),
        Index("idx_mock_interviews_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<MockInterviewModel id={self.id} role='{self.role}' score={self.score}>"
