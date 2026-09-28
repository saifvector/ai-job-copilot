import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.api_key import ApiKeyModel
from repositories.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKeyModel]):
    """
    Repository for managing third-party developer API keys and security metadata.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(model=ApiKeyModel, session=session)

    async def find_by_key_hash(self, key_hash: str) -> Optional[ApiKeyModel]:
        stmt = select(ApiKeyModel).where(
            ApiKeyModel.key_hash == key_hash,
            ApiKeyModel.is_active == True,
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ApiKeyModel], int]:
        stmt = (
            select(ApiKeyModel)
            .where(ApiKeyModel.user_id == user_id)
            .order_by(desc(ApiKeyModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(ApiKeyModel)
            .where(ApiKeyModel.user_id == user_id)
        )
        keys_res = await self.session.execute(stmt)
        count_res = await self.session.execute(count_stmt)
        return list(keys_res.scalars().all()), int(count_res.scalar() or 0)

    async def update_last_used(self, key_id: uuid.UUID) -> None:
        key = await self.get(key_id)
        if key:
            key.last_used_at = datetime.now(timezone.utc)
            await self.session.flush()

    async def revoke_key(self, key_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        stmt = select(ApiKeyModel).where(
            ApiKeyModel.id == key_id,
            ApiKeyModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        key = res.scalars().first()
        if not key:
            return False
        key.is_active = False
        key.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True
