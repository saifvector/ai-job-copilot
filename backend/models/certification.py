import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel


class CertificationModel(Base, UUIDPrimaryKeyMixin):
    """
    Certification model representing professional credentials and certifications.
    Table: certifications (Prisma mapped)
    """
    __tablename__ = "certifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to User
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="certifications",
        lazy="select",
    )


    __table_args__ = (
        Index("idx_certifications_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<CertificationModel id={self.id} user_id={self.user_id} name='{self.name}'>"
