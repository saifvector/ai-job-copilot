import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_authenticated_user_id, get_db
from schemas.platform import (
    WebhookCreate,
    WebhookDeliveryLogResponse,
    WebhookListResponse,
    WebhookResponse,
    WebhookTestRequest,
    WebhookTestResponse,
    WebhookUpdate,
)
from services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    body: WebhookCreate,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Register a new outbound webhook endpoint with event subscriptions."""
    service = WebhookService(db)
    try:
        webhook = await service.create_webhook(
            user_id=user_id,
            endpoint=body.endpoint,
            events=body.events,
            enabled=body.enabled if body.enabled is not None else True,
        )
        return webhook
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all registered webhook subscriptions for the current user."""
    service = WebhookService(db)
    items, total = await service.list_webhooks(user_id=user_id, limit=limit, offset=offset)
    return {"items": items, "total": total}


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details and secret for a specific webhook."""
    service = WebhookService(db)
    webhook = await service.repo.get_by_user_and_id(webhook_id, user_id)
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return webhook


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: uuid.UUID,
    body: WebhookUpdate,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update webhook endpoint URL, event triggers, or active status."""
    service = WebhookService(db)
    try:
        updated = await service.update_webhook(
            webhook_id=webhook_id,
            user_id=user_id,
            endpoint=body.endpoint,
            events=body.events,
            enabled=body.enabled,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete a webhook subscription."""
    service = WebhookService(db)
    deleted = await service.delete_webhook(webhook_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return None


@router.post("/{webhook_id}/test", response_model=WebhookTestResponse)
async def test_webhook(
    webhook_id: uuid.UUID,
    body: Optional[WebhookTestRequest] = None,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Send an immediate signed mock test payload to the webhook endpoint."""
    service = WebhookService(db)
    event_name = body.event if body and body.event else "job.matched"
    sample_payload = body.sample_payload if body else None
    try:
        result = await service.test_webhook(
            webhook_id=webhook_id,
            user_id=user_id,
            event=event_name,
            sample_payload=sample_payload,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{webhook_id}/deliveries")
async def list_webhook_deliveries(
    webhook_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List recent delivery logs, HTTP status codes, payloads, and retries."""
    service = WebhookService(db)
    items, total = await service.list_delivery_logs(webhook_id, user_id, limit=limit, offset=offset)
    return {"items": items, "total": total}
