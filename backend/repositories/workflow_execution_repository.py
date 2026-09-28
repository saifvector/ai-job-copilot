import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.workflow_execution import WorkflowExecutionModel
from repositories.base import BaseRepository


class WorkflowExecutionRepository(BaseRepository[WorkflowExecutionModel]):
    """
    Repository for storing and querying multi-agent workflow DAG executions.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WorkflowExecutionModel, session)

    async def create_execution(
        self,
        user_id: uuid.UUID,
        workflow_type: str,
        steps: List[Dict[str, Any]],
        initial_context: Dict[str, Any],
        execution_id: Optional[uuid.UUID] = None,
    ) -> WorkflowExecutionModel:
        execution = WorkflowExecutionModel(
            id=execution_id or uuid.uuid4(),
            user_id=user_id,
            workflow_type=workflow_type,
            status="PENDING",
            current_step=steps[0].get("step_id") if steps else None,
            steps=json.dumps(steps),
            context=json.dumps(initial_context),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(execution)
        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def update_progress(
        self,
        execution_id: uuid.UUID,
        status: str,
        current_step: Optional[str] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> Optional[WorkflowExecutionModel]:
        execution = await self.get_by_id(execution_id)
        if not execution:
            return None

        execution.status = status
        execution.updated_at = datetime.now(timezone.utc)
        if current_step is not None:
            execution.current_step = current_step
        if steps is not None:
            execution.steps = json.dumps(steps)
        if context is not None:
            execution.context = json.dumps(context)
        if duration_ms is not None:
            execution.duration_ms = duration_ms
        if status in ("COMPLETED", "FAILED", "CANCELLED"):
            execution.completed_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def complete_execution(
        self,
        execution_id: uuid.UUID,
        final_context: Dict[str, Any],
        step_records: List[Dict[str, Any]],
        duration_ms: Optional[float] = None,
    ) -> Optional[WorkflowExecutionModel]:
        return await self.update_progress(
            execution_id=execution_id,
            status="COMPLETED",
            current_step="FINISHED",
            steps=step_records,
            context=final_context,
            duration_ms=duration_ms,
        )

    async def fail_execution(
        self,
        execution_id: uuid.UUID,
        error: str,
        final_context: Dict[str, Any],
        step_records: List[Dict[str, Any]],
        duration_ms: Optional[float] = None,
    ) -> Optional[WorkflowExecutionModel]:
        ctx = dict(final_context)
        ctx["error"] = error
        return await self.update_progress(
            execution_id=execution_id,
            status="FAILED",
            current_step="FAILED",
            steps=step_records,
            context=ctx,
            duration_ms=duration_ms,
        )

    async def list_executions_filtered(
        self,
        user_id: uuid.UUID,
        workflow_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[WorkflowExecutionModel], int]:
        stmt = select(WorkflowExecutionModel).where(WorkflowExecutionModel.user_id == user_id)
        count_stmt = select(func.count(WorkflowExecutionModel.id)).where(WorkflowExecutionModel.user_id == user_id)

        if workflow_type:
            stmt = stmt.where(WorkflowExecutionModel.workflow_type == workflow_type)
            count_stmt = count_stmt.where(WorkflowExecutionModel.workflow_type == workflow_type)
        if status:
            stmt = stmt.where(WorkflowExecutionModel.status == status)
            count_stmt = count_stmt.where(WorkflowExecutionModel.status == status)

        stmt = stmt.order_by(desc(WorkflowExecutionModel.created_at)).offset(skip).limit(limit)

        rows = await self.session.execute(stmt)
        total_res = await self.session.execute(count_stmt)

        return list(rows.scalars().all()), int(total_res.scalar() or 0)
