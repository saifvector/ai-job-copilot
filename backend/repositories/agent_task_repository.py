import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.agent_task import AgentTaskModel
from repositories.base import BaseRepository


class AgentTaskRepository(BaseRepository[AgentTaskModel]):
    """
    Repository for storing, querying, and updating agent asynchronous tasks.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentTaskModel, session)

    async def create_task(
        self,
        agent: str,
        payload: Dict[str, Any],
        user_id: Optional[uuid.UUID] = None,
        workflow_execution_id: Optional[uuid.UUID] = None,
        model_override: Optional[str] = None,
        max_retries: int = 3,
    ) -> AgentTaskModel:
        task = AgentTaskModel(
            user_id=user_id,
            agent=agent,
            workflow_execution_id=workflow_execution_id,
            status="PENDING",
            payload=json.dumps(payload),
            model_used=model_override,
            max_retries=max_retries,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def update_status(
        self,
        task_id: uuid.UUID,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        model_used: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> Optional[AgentTaskModel]:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        task.status = status
        task.updated_at = datetime.now(timezone.utc)
        if result is not None:
            task.result = json.dumps(result)
        if error_message is not None:
            task.error_message = error_message
        if model_used is not None:
            task.model_used = model_used
        if duration_ms is not None:
            task.duration_ms = duration_ms
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            task.completed_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def increment_retry(self, task_id: uuid.UUID) -> Optional[AgentTaskModel]:
        task = await self.get_by_id(task_id)
        if not task:
            return None
        task.retry_count += 1
        task.status = "PENDING"
        task.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def list_tasks_filtered(
        self,
        user_id: Optional[uuid.UUID] = None,
        agent: Optional[str] = None,
        status: Optional[str] = None,
        workflow_execution_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgentTaskModel], int]:
        stmt = select(AgentTaskModel)
        count_stmt = select(func.count(AgentTaskModel.id))

        if user_id is not None:
            stmt = stmt.where(AgentTaskModel.user_id == user_id)
            count_stmt = count_stmt.where(AgentTaskModel.user_id == user_id)
        if agent:
            stmt = stmt.where(AgentTaskModel.agent == agent)
            count_stmt = count_stmt.where(AgentTaskModel.agent == agent)
        if status:
            stmt = stmt.where(AgentTaskModel.status == status)
            count_stmt = count_stmt.where(AgentTaskModel.status == status)
        if workflow_execution_id is not None:
            stmt = stmt.where(AgentTaskModel.workflow_execution_id == workflow_execution_id)
            count_stmt = count_stmt.where(AgentTaskModel.workflow_execution_id == workflow_execution_id)

        stmt = stmt.order_by(desc(AgentTaskModel.created_at)).offset(skip).limit(limit)

        rows = await self.session.execute(stmt)
        total_res = await self.session.execute(count_stmt)

        return list(rows.scalars().all()), int(total_res.scalar() or 0)
