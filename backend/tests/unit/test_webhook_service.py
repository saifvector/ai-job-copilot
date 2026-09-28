import uuid
import pytest
from services.webhook_service import WebhookService, SUPPORTED_WEBHOOK_EVENTS


@pytest.mark.asyncio
async def test_webhook_secret_and_signature_generation():
    secret = WebhookService.generate_secret()
    assert secret.startswith("whsec_")
    assert len(secret) > 20

    payload = '{"event":"job.matched","data":{"score":95.5}}'
    sig = WebhookService.sign_payload(payload, secret)

    assert "t=" in sig
    assert "v1=" in sig

    # Verify signature
    is_valid = WebhookService.verify_signature(
        payload_str=payload,
        signature_header=sig,
        secret=secret,
    )
    assert is_valid is True

    # Bad signature fails
    bad_sig = sig.replace("v1=", "v1=000000")
    assert WebhookService.verify_signature(payload, bad_sig, secret) is False

    # Tampered payload fails
    assert WebhookService.verify_signature(payload + "tamper", sig, secret) is False

    # Bad secret fails
    assert WebhookService.verify_signature(payload, sig, "whsec_wrong") is False


@pytest.mark.asyncio
async def test_webhook_lifecycle(db_session):
    service = WebhookService(db_session)
    user_id = uuid.uuid4()

    # 1. Create webhook
    wh = await service.create_webhook(
        user_id=user_id,
        endpoint="https://example.com/webhook/copilot",
        events=["job.matched", "application.created"],
    )

    assert wh.id is not None
    assert wh.endpoint == "https://example.com/webhook/copilot"
    assert wh.enabled is True
    assert "job.matched" in wh.events

    # 2. List webhooks
    items, total = await service.list_webhooks(user_id)
    assert total >= 1
    assert any(item.id == wh.id for item in items)

    # 3. Update webhook
    updated = await service.update_webhook(
        webhook_id=wh.id,
        user_id=user_id,
        enabled=False,
    )
    assert updated.enabled is False

    # 4. Delete webhook
    deleted = await service.delete_webhook(webhook_id=wh.id, user_id=user_id)
    assert deleted is True

    items_after, _ = await service.list_webhooks(user_id)
    assert not any(item.id == wh.id for item in items_after)


@pytest.mark.asyncio
async def test_webhook_event_filtering(db_session):
    service = WebhookService(db_session)
    user_id = uuid.uuid4()

    wh_matched = await service.create_webhook(
        user_id=user_id,
        endpoint="https://example.com/matches",
        events=["job.matched"],
    )
    wh_reports = await service.create_webhook(
        user_id=user_id,
        endpoint="https://example.com/reports",
        events=["report.generated"],
    )

    subscribers_matched = await service.repo.find_enabled_for_event(user_id=user_id, event="job.matched")
    matched_ids = [s.id for s in subscribers_matched]

    assert wh_matched.id in matched_ids
    assert wh_reports.id not in matched_ids
