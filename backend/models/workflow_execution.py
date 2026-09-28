import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel
    from models.agent_task import AgentTaskModel


class WorkflowExecutionModel(Base, UUIDPrimaryKeyMixin):
    """
    WorkflowExecutionModel stores multi-agent workflow DAG execution states, step outputs, and shared context.
    Table: workflow_executions
    """
    __tablename__ = "workflow_executions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    workflow_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    steps: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    context: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
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
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="workflow_executions")
    tasks: Mapped[List["AgentTaskModel"]] = relationship(
        "AgentTaskModel",
        back_populates="workflow_execution",
        cascade="all, delete-orphan",
        order_by="asc(AgentTaskModel.created_at)",
    )

    def __repr__(self) -> str:
        return f"<WorkflowExecutionModel id={self.id} type={self.workflow_type} status={self.status}>"
