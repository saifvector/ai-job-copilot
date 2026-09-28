import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.oauth_connection import OAuthConnectionModel
from repositories.base import BaseRepository


class OAuthConnectionRepository(BaseRepository[OAuthConnectionModel]):
    """
    Repository for managing OAuth integrations and synchronization metadata.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(model=OAuthConnectionModel, session=session)

    async def get_by_provider(self, user_id: uuid.UUID, provider: str) -> Optional[OAuthConnectionModel]:
        stmt = select(OAuthConnectionModel).where(
            OAuthConnectionModel.user_id == user_id,
            OAuthConnectionModel.provider == provider,
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_user(self, user_id: uuid.UUID) -> List[OAuthConnectionModel]:
        stmt = (
            select(OAuthConnectionModel)
            .where(OAuthConnectionModel.user_id == user_id)
            .order_by(OAuthConnectionModel.provider)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def upsert_connection(
        self,
        user_id: uuid.UUID,
        provider: str,
        provider_user_id: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        scopes: Optional[List[str]] = None,
        metadata_json: Optional[str] = None,
        status: str = "connected",
    ) -> OAuthConnectionModel:
        existing = await self.get_by_provider(user_id=user_id, provider=provider)
        if existing:
            existing.provider_user_id = provider_user_id or existing.provider_user_id
            existing.access_token = access_token or existing.access_token
            existing.refresh_token = refresh_token or existing.refresh_token
            existing.expires_at = expires_at or existing.expires_at
            existing.scopes = scopes if scopes is not None else existing.scopes
            existing.metadata_json = metadata_json or existing.metadata_json
            existing.status = status
            existing.updated_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        else:
            conn = OAuthConnectionModel(
                user_id=user_id,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                scopes=scopes or [],
                metadata_json=metadata_json,
                status=status,
            )
            self.session.add(conn)
            await self.session.flush()
            await self.session.refresh(conn)
            return conn

    async def disconnect(self, user_id: uuid.UUID, provider: str) -> bool:
        conn = await self.get_by_provider(user_id=user_id, provider=provider)
        if not conn:
            return False
        conn.status = "disconnected"
        conn.access_token = None
        conn.refresh_token = None
        conn.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True
