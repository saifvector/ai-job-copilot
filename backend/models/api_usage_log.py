import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Float, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base, UUIDPrimaryKeyMixin


class ApiUsageLogModel(Base, UUIDPrimaryKeyMixin):
    """
    ApiUsageLog model stores telemetry on every developer or public API invocation.
    Table: api_usage_logs
    """
    __tablename__ = "api_usage_logs"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    api_key_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), nullable=True, index=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<ApiUsageLogModel endpoint={self.endpoint} status={self.status_code} latency={self.latency_ms}ms>"
