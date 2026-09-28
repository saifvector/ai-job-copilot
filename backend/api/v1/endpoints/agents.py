import logging
import uuid
from typing import Optional

logger = logging.getLogger(__name__)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_authenticated_user_id, get_db
from orchestration.model_router import model_router
from schemas.agent_orchestration import (
    AgentExecuteRequest,
    AgentExecuteResponse,
    AgentInfoResponse,
    AgentListResponse,
    AgentMemoryCreate,
    AgentMemoryListResponse,
    AgentMemoryResponse,
    ModelRouteRequest,
    ModelRouteResponse,
)
from services.agent_orchestration_service import AgentOrchestrationService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=AgentListResponse)
async def list_agents(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """List all registered specialized AI agents with capabilities and operating statuses."""
    service = AgentOrchestrationService(db)
    agents = service.list_agents()
    return {"items": agents, "total": len(agents)}


@router.get("/memories", response_model=AgentMemoryListResponse)
async def list_agent_memories(
    agent: Optional[str] = Query(None, description="Filter by agent name"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retrieve persistent agent shared memories and working contexts."""
    service = AgentOrchestrationService(db)
    items, total = await service.list_agent_memories_paginated(
        user_id=user_id,
        agent=agent,
        skip=skip,
        limit=limit,
    )
    return {"items": items, "total": total}


@router.post("/memories", response_model=AgentMemoryResponse, status_code=status.HTTP_201_CREATED)
async def store_agent_memory(
    body: AgentMemoryCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Persist context or critique into agent memory for downstream cross-agent reuse."""
    service = AgentOrchestrationService(db)
    try:
        mem = await service.store_agent_memory(
            user_id=user_id,
            agent=body.agent,
            memory_type=body.memory_type,
            content=body.content,
            relevance_score=body.relevance_score or 1.0,
        )
        return mem
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/model-route", response_model=ModelRouteResponse)
async def route_model(
    body: ModelRouteRequest,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Simulate model routing based on speed, cost, complexity, and privacy preferences."""
    routed = model_router.route(
        task_type=body.task_type,
        complexity=body.complexity,
        speed_preference=body.speed_preference,
        cost_preference=body.cost_preference,
        privacy_level=body.privacy_level,
    )
    return routed


@router.get("/{agent_name}", response_model=AgentInfoResponse)
async def get_agent(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Retrieve metadata and capabilities for a specific specialized agent."""
    service = AgentOrchestrationService(db)
    agent = service.get_agent(agent_name)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_name}' is not registered.",
        )
    return {
        "name": agent.agent_name,
        "description": agent.description,
        "capabilities": agent.capabilities,
        "default_model": agent.default_model,
        "status": agent.status,
    }


@router.post("/{agent_name}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_name: str,
    body: AgentExecuteRequest,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
):
    """Synchronously execute a specialized AI agent with direct payload and context."""
    service = AgentOrchestrationService(db)
    try:
        res = await service.execute_agent_direct(
            agent_name=agent_name,
            payload=body.payload,
            user_id=user_id,
            model_override=body.model_override,
            persist_memory=True,
        )
        return res
    except ValueError as e:
        logger.error(f"[execute_agent] ValueError: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"[execute_agent] Exception: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
