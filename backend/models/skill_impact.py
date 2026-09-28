import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class SkillImpactModel(Base, UUIDPrimaryKeyMixin):
    """
    SkillImpactModel tracks the descriptive statistical correlation between individual candidate skills
    and successful job search outcomes (interviews influenced, offers influenced, average match score).
    Table: skill_impacts
    """
    __tablename__ = "skill_impacts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    interviews_influenced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    offers_influenced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_match_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
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
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="skill_impacts")

    __table_args__ = (
        UniqueConstraint("user_id", "skill_name", name="uq_skill_impacts_user_skill"),
        Index("idx_skill_impacts_user_id", "user_id"),
        Index("idx_skill_impacts_skill_name", "skill_name"),
        Index("idx_skill_impacts_interviews", "interviews_influenced"),
    )

    def __repr__(self) -> str:
        return f"<SkillImpactModel skill='{self.skill_name}' interviews={self.interviews_influenced} offers={self.offers_influenced}>"
