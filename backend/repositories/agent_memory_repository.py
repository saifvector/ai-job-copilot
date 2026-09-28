import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.agent_memory import AgentMemoryModel
from repositories.base import BaseRepository


class AgentMemoryRepository(BaseRepository[AgentMemoryModel]):
    """
    Repository for persisting, retrieving, and ranking agent shared memories.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentMemoryModel, session)

    async def store_memory(
        self,
        user_id: uuid.UUID,
        agent: str,
        memory_type: str,
        content: Dict[str, Any],
        relevance_score: float = 1.0,
    ) -> AgentMemoryModel:
        mem = AgentMemoryModel(
            user_id=user_id,
            agent=agent,
            memory_type=memory_type,
            content=json.dumps(content),
            relevance_score=relevance_score,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(mem)
        await self.session.flush()
        await self.session.refresh(mem)
        return mem

    async def retrieve_memories(
        self,
        user_id: uuid.UUID,
        agent: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[AgentMemoryModel]:
        stmt = select(AgentMemoryModel).where(AgentMemoryModel.user_id == user_id)

        if agent:
            # Match agent specifically or global '*' memories
            stmt = stmt.where(or_(AgentMemoryModel.agent == agent, AgentMemoryModel.agent == "*"))
        if memory_type:
            stmt = stmt.where(AgentMemoryModel.memory_type == memory_type)

        stmt = stmt.order_by(
            desc(AgentMemoryModel.relevance_score),
            desc(AgentMemoryModel.created_at),
        ).limit(limit)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_memories_paginated(
        self,
        user_id: uuid.UUID,
        agent: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AgentMemoryModel], int]:
        stmt = select(AgentMemoryModel).where(AgentMemoryModel.user_id == user_id)
        count_stmt = select(func.count(AgentMemoryModel.id)).where(AgentMemoryModel.user_id == user_id)

        if agent:
            stmt = stmt.where(or_(AgentMemoryModel.agent == agent, AgentMemoryModel.agent == "*"))
            count_stmt = count_stmt.where(or_(AgentMemoryModel.agent == agent, AgentMemoryModel.agent == "*"))

        stmt = stmt.order_by(desc(AgentMemoryModel.created_at)).offset(skip).limit(limit)

        rows = await self.session.execute(stmt)
        total_res = await self.session.execute(count_stmt)

        return list(rows.scalars().all()), int(total_res.scalar() or 0)
