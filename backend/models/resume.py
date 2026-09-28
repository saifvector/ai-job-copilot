import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel
    from models.tailored_resume import TailoredResumeModel


class ResumeModel(Base, UUIDPrimaryKeyMixin):
    """
    Resume database model tracking candidate resume documents and storage paths.
    Table: resumes (Prisma mapped)
    """
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
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

    # 1-to-1 Relationship back to UserModel
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="resume",
        lazy="joined",
    )

    # 1-to-many Relationship with TailoredResumeModel
    tailored_resumes: Mapped[List["TailoredResumeModel"]] = relationship(
        "TailoredResumeModel",
        back_populates="original_resume",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_resumes_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ResumeModel id={self.id} user_id={self.user_id} filename='{self.original_filename}'>"
