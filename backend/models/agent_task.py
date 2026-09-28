import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.user import UserModel
    from models.workflow_execution import WorkflowExecutionModel


class AgentTaskModel(Base, UUIDPrimaryKeyMixin):
    """
    AgentTaskModel represents an asynchronous unit of work executed by a specialized AI agent.
    Table: agent_tasks
    """
    __tablename__ = "agent_tasks"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    agent: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    workflow_execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workflow_executions.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
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
    user: Mapped[Optional["UserModel"]] = relationship("UserModel", back_populates="agent_tasks")
    workflow_execution: Mapped[Optional["WorkflowExecutionModel"]] = relationship(
        "WorkflowExecutionModel",
        back_populates="tasks",
    )

    def __repr__(self) -> str:
        return f"<AgentTaskModel id={self.id} agent={self.agent} status={self.status}>"
