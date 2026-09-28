import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class SkillModel(Base, UUIDPrimaryKeyMixin):
    """
    Skill model representing candidate competencies extracted from resumes.
    Categories: Programming Language, Framework, Database, Cloud, AI/ML, Tool, Other
    Table: skills (Prisma mapped)
    """
    __tablename__ = "skills"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="Other")
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to User
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="skills",
        lazy="select",
    )


    __table_args__ = (
        Index("idx_skills_user_id", "user_id"),
        Index("idx_skills_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<SkillModel id={self.id} user_id={self.user_id} name='{self.name}' category='{self.category}'>"
