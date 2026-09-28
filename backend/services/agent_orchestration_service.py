import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base import BaseAgent
from agents.registry import agent_registry
from models.agent_memory import AgentMemoryModel
from models.agent_task import AgentTaskModel
from models.workflow_execution import WorkflowExecutionModel
from orchestration.event_bus import AgentEvent, event_bus
from orchestration.workflow_engine import workflow_engine
from repositories.agent_memory_repository import AgentMemoryRepository
from repositories.agent_task_repository import AgentTaskRepository
from repositories.workflow_execution_repository import WorkflowExecutionRepository
from services.base import BaseService

logger = logging.getLogger(__name__)


class AgentOrchestrationService:
    """
    Central orchestration and management service for AI agents, multi-agent workflows,
    asynchronous task lifecycles, and shared memory storage.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repo = AgentTaskRepository(session)
        self.memory_repo = AgentMemoryRepository(session)
        self.workflow_repo = WorkflowExecutionRepository(session)

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def list_agents(self) -> List[Dict[str, Any]]:
        return agent_registry.list_agents()

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        return agent_registry.get(agent_name)

    async def execute_agent_direct(
        self,
        agent_name: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None,
        model_override: Optional[str] = None,
        persist_memory: bool = False,
    ) -> Dict[str, Any]:
        agent = agent_registry.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' is not registered.")

        # Enrich context with past agent memories if user_id is provided
        merged_context = dict(context or {})
        if user_id:
            past_mems = await self.memory_repo.retrieve_memories(
                user_id=user_id,
                agent=agent_name,
                limit=5,
            )
            if past_mems:
                merged_context["agent_memories"] = [
                    json.loads(m.content) if isinstance(m.content, str) else m.content
                    for m in past_mems
                ]

        execution_result = await agent.execute(
            payload=payload,
            context=merged_context,
            user_id=user_id,
            session=self.session,
            model_override=model_override,
        )

        # Optionally persist output into agent memory
        if persist_memory and user_id:
            await self.memory_repo.store_memory(
                user_id=user_id,
                agent=agent_name,
                memory_type="execution_output",
                content=execution_result.get("result", {}),
                relevance_score=1.0,
            )
            await self.session.commit()

        return execution_result

    # =========================================================================
    # TASK SYSTEM & BACKGROUND EXECUTION
    # =========================================================================

    async def create_task(
        self,
        agent: str,
        payload: Dict[str, Any],
        user_id: Optional[uuid.UUID] = None,
        workflow_execution_id: Optional[uuid.UUID] = None,
        model_override: Optional[str] = None,
        max_retries: int = 3,
    ) -> AgentTaskModel:
        if not agent_registry.has(agent):
            raise ValueError(f"Cannot dispatch task: agent '{agent}' is not registered.")

        task = await self.task_repo.create_task(
            agent=agent,
            payload=payload,
            user_id=user_id,
            workflow_execution_id=workflow_execution_id,
            model_override=model_override,
            max_retries=max_retries,
        )
        await self.session.commit()

        await event_bus.publish(
            AgentEvent(
                event_name="TaskCreated",
                user_id=user_id,
                payload={
                    "task_id": str(task.id),
                    "agent": agent,
                    "status": "PENDING",
                },
            )
        )
        return task

    async def run_task(self, task_id: uuid.UUID) -> AgentTaskModel:
        """
        Executes a pending agent task, handles retries, updates status, and emits events.
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task '{task_id}' not found.")

        agent = agent_registry.get(task.agent)
        if not agent:
            await self.task_repo.update_status(
                task_id=task.id,
                status="FAILED",
                error_message=f"Agent '{task.agent}' is not registered.",
            )
            await self.session.commit()
            return task

        # Mark as RUNNING
        await self.task_repo.update_status(task_id=task.id, status="RUNNING")
        await self.session.commit()

        start_time = time.perf_counter()
        parsed_payload = json.loads(task.payload) if isinstance(task.payload, str) else (task.payload or {})

        try:
            res = await agent.execute(
                payload=parsed_payload,
                context={},
                user_id=task.user_id,
                session=self.session,
                model_override=task.model_used,
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            task = await self.task_repo.update_status(
                task_id=task.id,
                status="COMPLETED",
                result=res.get("result", {}),
                model_used=res.get("model_used"),
                duration_ms=duration_ms,
            )
            await self.session.commit()

            await event_bus.publish(
                AgentEvent(
                    event_name="TaskCompleted",
                    user_id=task.user_id,
                    payload={
                        "task_id": str(task.id),
                        "agent": task.agent,
                        "status": "COMPLETED",
                        "duration_ms": duration_ms,
                    },
                )
            )
            return task

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            err_msg = str(exc)
            logger.error(f"[AgentOrchestrationService] Task {task_id} failed: {err_msg}", exc_info=True)

            # Check if retryable
            if task.retry_count < task.max_retries:
                task = await self.task_repo.increment_retry(task_id=task.id)
            else:
                task = await self.task_repo.update_status(
                    task_id=task.id,
                    status="FAILED",
                    error_message=err_msg,
                    duration_ms=duration_ms,
                )

            await self.session.commit()

            await event_bus.publish(
                AgentEvent(
                    event_name="TaskFailed",
                    user_id=task.user_id,
                    payload={
                        "task_id": str(task.id),
                        "agent": task.agent,
                        "status": task.status,
                        "retry_count": task.retry_count,
                        "error": err_msg,
                    },
                )
            )
            return task

    async def list_tasks(
        self,
        user_id: Optional[uuid.UUID] = None,
        agent: Optional[str] = None,
        status: Optional[str] = None,
        workflow_execution_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgentTaskModel], int]:
        return await self.task_repo.list_tasks_filtered(
            user_id=user_id,
            agent=agent,
            status=status,
            workflow_execution_id=workflow_execution_id,
            skip=skip,
            limit=limit,
        )

    async def get_task(self, task_id: uuid.UUID) -> Optional[AgentTaskModel]:
        return await self.task_repo.get_by_id(task_id)

    async def retry_task(self, task_id: uuid.UUID) -> Optional[AgentTaskModel]:
        task = await self.task_repo.increment_retry(task_id)
        if task:
            await self.session.commit()
            # Dispatch asynchronous run
            asyncio.create_task(self.run_task(task.id))
        return task

    async def cancel_task(self, task_id: uuid.UUID) -> Optional[AgentTaskModel]:
        task = await self.task_repo.update_status(task_id, status="CANCELLED")
        if task:
            await self.session.commit()
        return task

    # =========================================================================
    # AGENT MEMORY
    # =========================================================================

    async def store_agent_memory(
        self,
        user_id: uuid.UUID,
        agent: str,
        memory_type: str,
        content: Dict[str, Any],
        relevance_score: float = 1.0,
    ) -> AgentMemoryModel:
        mem = await self.memory_repo.store_memory(
            user_id=user_id,
            agent=agent,
            memory_type=memory_type,
            content=content,
            relevance_score=relevance_score,
        )
        await self.session.commit()
        return mem

    async def retrieve_agent_memories(
        self,
        user_id: uuid.UUID,
        agent: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[AgentMemoryModel]:
        return await self.memory_repo.retrieve_memories(
            user_id=user_id,
            agent=agent,
            memory_type=memory_type,
            limit=limit,
        )

    async def list_agent_memories_paginated(
        self,
        user_id: uuid.UUID,
        agent: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgentMemoryModel], int]:
        return await self.memory_repo.list_memories_paginated(
            user_id=user_id,
            agent=agent,
            skip=skip,
            limit=limit,
        )

    # =========================================================================
    # WORKFLOW SYSTEM
    # =========================================================================

    def list_workflows(self) -> List[Dict[str, Any]]:
        return workflow_engine.list_workflow_templates()

    def get_workflow_template(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return workflow_engine.get_workflow_template(workflow_id)

    async def execute_workflow(
        self,
        workflow_id: str,
        user_id: Optional[uuid.UUID] = None,
        initial_context: Optional[Dict[str, Any]] = None,
        custom_steps: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        execution_id = uuid.uuid4()
        return await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            initial_context=initial_context,
            custom_steps=custom_steps,
            user_id=user_id,
            execution_id=execution_id,
            session=self.session,
        )

    async def get_workflow_execution(self, execution_id: uuid.UUID) -> Optional[WorkflowExecutionModel]:
        return await self.workflow_repo.get_by_id(execution_id)

    async def list_workflow_executions(
        self,
        user_id: uuid.UUID,
        workflow_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[WorkflowExecutionModel], int]:
        return await self.workflow_repo.list_executions_filtered(
            user_id=user_id,
            workflow_type=workflow_type,
            status=status,
            skip=skip,
            limit=limit,
        )

    # =========================================================================
    # OBSERVABILITY TELEMETRY
    # =========================================================================

    async def get_observability_metrics(self, user_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        tasks, total_tasks = await self.task_repo.list_tasks_filtered(user_id=user_id, limit=200)

        completed_tasks = [t for t in tasks if t.status == "COMPLETED"]
        failed_tasks = [t for t in tasks if t.status == "FAILED"]
        running_tasks = [t for t in tasks if t.status == "RUNNING"]
        pending_tasks = [t for t in tasks if t.status == "PENDING"]

        durations = [t.duration_ms for t in completed_tasks if t.duration_ms is not None]
        avg_duration_ms = round(sum(durations) / len(durations), 2) if durations else 0.0

        # Model routing stats
        model_usage: Dict[str, int] = {}
        for t in tasks:
            if t.model_used:
                model_usage[t.model_used] = model_usage.get(t.model_used, 0) + 1

        total_done = len(completed_tasks) + len(failed_tasks)
        failure_rate = round((len(failed_tasks) / total_done * 100), 2) if total_done > 0 else 0.0

        # Registered agents summary
        registered_agents = agent_registry.list_agents()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "running_tasks": len(running_tasks),
            "pending_tasks": len(pending_tasks),
            "avg_duration_ms": avg_duration_ms,
            "failure_rate_pct": failure_rate,
            "model_usage": model_usage,
            "registered_agents_count": len(registered_agents),
            "active_workflows_count": len(workflow_engine.list_workflow_templates()),
        }
