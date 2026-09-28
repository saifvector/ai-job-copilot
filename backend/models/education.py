import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class EducationModel(Base, UUIDPrimaryKeyMixin):
    """
    Education model representing candidate degree and institution background.
    Table: education (Prisma mapped)
    """
    __tablename__ = "education"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to User
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="education",
        lazy="select",
    )


    __table_args__ = (
        Index("idx_education_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<EducationModel id={self.id} user_id={self.user_id} institution='{self.institution}' degree='{self.degree}'>"
