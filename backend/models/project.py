import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class ProjectModel(Base, UUIDPrimaryKeyMixin):
    """
    Project model representing portfolio and technical projects.
    Table: projects (Prisma mapped)
    """
    __tablename__ = "projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    technologies: Mapped[List[str]] = mapped_column(
        ARRAY(String).with_variant(JSON, "sqlite"),
        nullable=False,
        default=list,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to User
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="projects",
        lazy="select",
    )


    __table_args__ = (
        Index("idx_projects_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ProjectModel id={self.id} user_id={self.user_id} title='{self.title}'>"
