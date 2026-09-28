import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from models.webhook import WebhookDeliveryLogModel, WebhookModel
from repositories.webhook_repository import WebhookRepository

logger = logging.getLogger(__name__)

SUPPORTED_WEBHOOK_EVENTS = [
    "resume.parsed",
    "job.matched",
    "report.generated",
    "application.created",
    "application.updated",
]


class WebhookService:
    """
    Manages Webhook subscriptions, cryptographic HMAC-SHA256 signature generation/verification,
    and reliable asynchronous event dispatch with retries.
    """

    @staticmethod
    def generate_secret() -> str:
        """Generates a secure random HMAC secret."""
        return f"whsec_{secrets.token_hex(24)}"

    @staticmethod
    def sign_payload(payload_str: str, secret: str, timestamp: Optional[int] = None) -> str:
        """
        Generates HMAC-SHA256 timestamped signature matching Stripe / GitHub standard format:
        t=1672531199,v1=9a8b7c...
        """
        ts = timestamp if timestamp is not None else int(time.time())
        signature_payload = f"{ts}.{payload_str}".encode("utf-8")
        computed_hmac = hmac.new(
            secret.encode("utf-8"),
            signature_payload,
            hashlib.sha256,
        ).hexdigest()
        return f"t={ts},v1={computed_hmac}"

    @staticmethod
    def verify_signature(
        payload_str: str,
        signature_header: str,
        secret: str,
        tolerance_seconds: int = 300,
    ) -> bool:
        """
        Verifies timestamp and HMAC-SHA256 signature using constant-time comparison.
        Prevents replay attacks older than tolerance_seconds.
        """
        if not signature_header or not secret:
            return False

        try:
            parts = dict(part.split("=", 1) for part in signature_header.split(","))
            if "t" not in parts or "v1" not in parts:
                return False

            timestamp = int(parts["t"])
            received_signature = parts["v1"]

            # Replay attack prevention
            current_time = int(time.time())
            if abs(current_time - timestamp) > tolerance_seconds:
                return False

            expected_sig = WebhookService.sign_payload(payload_str, secret, timestamp=timestamp)
            expected_v1 = expected_sig.split("v1=")[1]
            return hmac.compare_digest(received_signature, expected_v1)
        except Exception as exc:
            logger.warning(f"Webhook signature verification failed: {exc}")
            return False

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WebhookRepository(session)

    async def create_webhook(
        self,
        user_id: uuid.UUID,
        endpoint: str,
        events: List[str],
        enabled: bool = True,
    ) -> WebhookModel:
        # Validate events
        invalid_events = [e for e in events if e not in SUPPORTED_WEBHOOK_EVENTS]
        if invalid_events:
            raise ValueError(f"Unsupported webhook events: {invalid_events}")

        secret = self.generate_secret()
        webhook = WebhookModel(
            user_id=user_id,
            endpoint=endpoint,
            secret=secret,
            events=events,
            enabled=enabled,
        )
        return await self.repo.create(webhook)

    async def update_webhook(
        self,
        webhook_id: uuid.UUID,
        user_id: uuid.UUID,
        endpoint: Optional[str] = None,
        events: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[WebhookModel]:
        webhook = await self.repo.get_by_user_and_id(webhook_id, user_id)
        if not webhook:
            return None

        if endpoint is not None:
            webhook.endpoint = endpoint
        if events is not None:
            invalid_events = [e for e in events if e not in SUPPORTED_WEBHOOK_EVENTS]
            if invalid_events:
                raise ValueError(f"Unsupported webhook events: {invalid_events}")
            webhook.events = events
        if enabled is not None:
            webhook.enabled = enabled

        webhook.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return webhook

    async def delete_webhook(self, webhook_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        webhook = await self.repo.get_by_user_and_id(webhook_id, user_id)
        if not webhook:
            return False
        await self.session.delete(webhook)
        await self.session.flush()
        return True

    async def list_webhooks(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WebhookModel], int]:
        return await self.repo.list_by_user(user_id=user_id, limit=limit, offset=offset)

    async def list_delivery_logs(
        self,
        webhook_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WebhookDeliveryLogModel], int]:
        webhook = await self.repo.get_by_user_and_id(webhook_id, user_id)
        if not webhook:
            return [], 0
        return await self.repo.list_delivery_logs(webhook_id=webhook_id, limit=limit, offset=offset)

    async def dispatch_event(
        self,
        user_id: uuid.UUID,
        event: str,
        data: Dict[str, Any],
        max_retries: int = 3,
    ) -> List[WebhookDeliveryLogModel]:
        """
        Finds all active webhooks subscribing to the given event for this user,
        builds the signed payload, and executes delivery with exponential backoff retries.
        """
        webhooks = await self.repo.find_enabled_for_event(user_id=user_id, event=event)
        if not webhooks:
            return []

        payload_obj = {
            "id": f"evt_{uuid.uuid4().hex[:16]}",
            "event": event,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        payload_str = json.dumps(payload_obj, default=str)

        delivery_logs = []
        for wh in webhooks:
            log = await self._deliver_with_retry(
                webhook=wh,
                event=event,
                payload_str=payload_str,
                max_retries=max_retries,
            )
            delivery_logs.append(log)

        return delivery_logs

    async def test_webhook(
        self,
        webhook_id: uuid.UUID,
        user_id: uuid.UUID,
        event: str = "job.matched",
        sample_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Sends a test ping to the specified webhook endpoint."""
        webhook = await self.repo.get_by_user_and_id(webhook_id, user_id)
        if not webhook:
            raise ValueError("Webhook subscription not found")

        data = sample_payload or {
            "test": True,
            "message": f"Webhook test ping for event: {event}",
            "job": {
                "id": str(uuid.uuid4()),
                "title": "Senior Platform Engineer",
                "company": "Tech Corp",
                "overall_score": 92.5,
            }
        }
        payload_obj = {
            "id": f"evt_test_{uuid.uuid4().hex[:12]}",
            "event": event,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        payload_str = json.dumps(payload_obj, default=str)
        signature = self.sign_payload(payload_str, webhook.secret)

        start_time = time.perf_counter()
        status_code = None
        error_msg = None
        success = False

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Job-Copilot-Webhook/1.0",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(webhook.endpoint, content=payload_str, headers=headers)
                status_code = res.status_code
                success = 200 <= status_code < 300
                response_text = res.text[:1000]
        except Exception as exc:
            error_msg = str(exc)
            response_text = None

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Record test delivery in logs
        await self.repo.create_delivery_log(
            webhook_id=webhook.id,
            event=event,
            payload=payload_str,
            response_status=status_code,
            response_body=response_text,
            duration_ms=duration_ms,
            attempt=1,
            success=success,
            error=error_msg,
        )

        return {
            "success": success,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "error": error_msg,
            "signature": signature,
        }

    async def _deliver_with_retry(
        self,
        webhook: WebhookModel,
        event: str,
        payload_str: str,
        max_retries: int = 3,
    ) -> WebhookDeliveryLogModel:
        signature = self.sign_payload(payload_str, webhook.secret)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Job-Copilot-Webhook/1.0",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event": event,
        }

        last_status = None
        last_body = None
        last_error = None
        duration_ms = 0.0
        success = False

        for attempt in range(1, max_retries + 1):
            start = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    response = await client.post(webhook.endpoint, content=payload_str, headers=headers)
                    duration_ms = round((time.perf_counter() - start) * 1000, 2)
                    last_status = response.status_code
                    last_body = response.text[:1000]

                    if 200 <= response.status_code < 300:
                        success = True
                        webhook.failure_count = 0
                        break
                    else:
                        last_error = f"HTTP {response.status_code}"
            except Exception as e:
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                last_error = str(e)

            # Exponential backoff retry delay (0.05s * 2^attempt for tests and high throughput)
            if attempt < max_retries:
                await asyncio.sleep(0.05 * (2 ** attempt))

        if not success:
            webhook.failure_count += 1
            if webhook.failure_count >= 10:
                webhook.enabled = False
                logger.warning(f"Webhook {webhook.id} disabled after 10 consecutive delivery failures")

        await self.session.flush()

        log = await self.repo.create_delivery_log(
            webhook_id=webhook.id,
            event=event,
            payload=payload_str,
            response_status=last_status,
            response_body=last_body,
            duration_ms=duration_ms,
            attempt=attempt,
            success=success,
            error=last_error,
        )
        return log
