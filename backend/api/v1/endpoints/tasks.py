import asyncio
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_authenticated_user_id, get_db
from schemas.agent_orchestration import (
    AgentTaskCreate,
    AgentTaskListResponse,
    AgentTaskResponse,
)
from services.agent_orchestration_service import AgentOrchestrationService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=AgentTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: AgentTaskCreate,
    run_async: bool = Query(default=True, description="Execute immediately in background"),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Enqueue a new specialized agent background task."""
    service = AgentOrchestrationService(db)
    try:
        task = await service.create_task(
            agent=body.agent,
            payload=body.payload,
            user_id=user_id,
            model_override=body.model_override,
        )
        if run_async:
            # Dispatch asynchronous worker execution
            asyncio.create_task(service.run_task(task.id))
        return task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=AgentTaskListResponse)
async def list_tasks(
    agent: Optional[str] = Query(None, description="Filter by agent name"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """List agent tasks for current authenticated user."""
    service = AgentOrchestrationService(db)
    items, total = await service.list_tasks(
        user_id=user_id,
        agent=agent,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total}


@router.get("/{task_id}", response_model=AgentTaskResponse)
async def get_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retrieve detailed state and result of a specific agent task."""
    service = AgentOrchestrationService(db)
    task = await service.get_task(task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")
    return task


@router.post("/{task_id}/retry", response_model=AgentTaskResponse)
async def retry_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retry a failed agent task."""
    service = AgentOrchestrationService(db)
    task = await service.get_task(task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")
    retried = await service.retry_task(task_id)
    return retried


@router.post("/{task_id}/cancel", response_model=AgentTaskResponse)
async def cancel_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Cancel an active or pending agent task."""
    service = AgentOrchestrationService(db)
    task = await service.get_task(task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")
    cancelled = await service.cancel_task(task_id)
    return cancelled
