import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_authenticated_user_id, get_db
from schemas.agent_orchestration import (
    WorkflowDefinitionResponse,
    WorkflowExecuteRequest,
    WorkflowExecutionListResponse,
    WorkflowExecutionResponse,
)
from services.agent_orchestration_service import AgentOrchestrationService

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """List all pre-configured multi-agent workflow DAG templates."""
    service = AgentOrchestrationService(db)
    return service.list_workflows()


@router.get("/telemetry/metrics")
async def get_orchestration_telemetry(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retrieve aggregate observability telemetry, model usage, and task completion metrics."""
    service = AgentOrchestrationService(db)
    return await service.get_observability_metrics(user_id=user_id)


@router.get("/executions", response_model=WorkflowExecutionListResponse)
async def list_workflow_executions(
    workflow_type: Optional[str] = Query(None, description="Filter by workflow template"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """List past and running workflow pipeline executions."""
    service = AgentOrchestrationService(db)
    items, total = await service.list_workflow_executions(
        user_id=user_id,
        workflow_type=workflow_type,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total}


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retrieve detailed execution trace, current step, step records, and shared context."""
    service = AgentOrchestrationService(db)
    execution = await service.get_workflow_execution(execution_id)
    if not execution or execution.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow execution '{execution_id}' not found.",
        )
    return execution


@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow_template(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retrieve workflow DAG definition and step specifications."""
    service = AgentOrchestrationService(db)
    template = service.get_workflow_template(workflow_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow template '{workflow_id}' not found.",
        )
    return template


@router.post("/execute", response_model=Dict[str, Any])
async def execute_workflow(
    body: WorkflowExecuteRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Execute a multi-agent workflow pipeline end-to-end with shared context propagation."""
    service = AgentOrchestrationService(db)
    try:
        result = await service.execute_workflow(
            workflow_id=body.workflow_type,
            user_id=user_id,
            initial_context=body.initial_context,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
