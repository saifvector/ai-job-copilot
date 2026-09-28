import uuid
from typing import List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.webhook import WebhookModel, WebhookDeliveryLogModel
from repositories.base import BaseRepository


class WebhookRepository(BaseRepository[WebhookModel]):
    """
    Repository for managing Webhooks and delivery logs.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(model=WebhookModel, session=session)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WebhookModel], int]:
        stmt = (
            select(WebhookModel)
            .where(WebhookModel.user_id == user_id)
            .order_by(desc(WebhookModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(WebhookModel)
            .where(WebhookModel.user_id == user_id)
        )
        webhooks_res = await self.session.execute(stmt)
        count_res = await self.session.execute(count_stmt)
        return list(webhooks_res.scalars().all()), int(count_res.scalar() or 0)

    async def get_by_user_and_id(self, webhook_id: uuid.UUID, user_id: uuid.UUID) -> Optional[WebhookModel]:
        stmt = select(WebhookModel).where(
            WebhookModel.id == webhook_id,
            WebhookModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def find_enabled_for_event(self, user_id: uuid.UUID, event: str) -> List[WebhookModel]:
        """Finds all active webhooks for a user that subscribe to this event."""
        stmt = select(WebhookModel).where(
            WebhookModel.user_id == user_id,
            WebhookModel.enabled == True,
        )
        res = await self.session.execute(stmt)
        all_webhooks = res.scalars().all()
        # Filter matching events in python to ensure cross-DB (sqlite and postgres) consistency
        return [wh for wh in all_webhooks if not wh.events or event in wh.events]

    async def create_delivery_log(
        self,
        webhook_id: uuid.UUID,
        event: str,
        payload: str,
        response_status: Optional[int] = None,
        response_body: Optional[str] = None,
        duration_ms: Optional[float] = None,
        attempt: int = 1,
        success: bool = False,
        error: Optional[str] = None,
    ) -> WebhookDeliveryLogModel:
        log = WebhookDeliveryLogModel(
            webhook_id=webhook_id,
            event=event,
            payload=payload,
            response_status=response_status,
            response_body=response_body,
            duration_ms=duration_ms,
            attempt=attempt,
            success=success,
            error=error,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def list_delivery_logs(
        self,
        webhook_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WebhookDeliveryLogModel], int]:
        stmt = (
            select(WebhookDeliveryLogModel)
            .where(WebhookDeliveryLogModel.webhook_id == webhook_id)
            .order_by(desc(WebhookDeliveryLogModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(WebhookDeliveryLogModel)
            .where(WebhookDeliveryLogModel.webhook_id == webhook_id)
        )
        logs_res = await self.session.execute(stmt)
        count_res = await self.session.execute(count_stmt)
        return list(logs_res.scalars().all()), int(count_res.scalar() or 0)
