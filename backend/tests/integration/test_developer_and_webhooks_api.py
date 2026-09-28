import uuid
import pytest
from httpx import AsyncClient
from models.user import UserModel


@pytest.mark.asyncio
async def test_developer_api_keys_and_analytics(client: AsyncClient, db_session):
    # Ensure test user exists
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Developer Portal Tester",
        email=f"dev_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"X-User-Id": str(user_id)}

    # 1. Create API Key
    create_res = await client.post(
        "/api/v1/developer/keys",
        json={"name": "Zapier Webhooks Key", "scopes": ["read:profile", "read:matches"]},
        headers=headers,
    )
    assert create_res.status_code == 201
    key_data = create_res.json()
    assert "raw_key" in key_data
    assert key_data["raw_key"].startswith("ajc_live_")
    key_id = key_data["id"]

    # 2. List API Keys
    list_res = await client.get("/api/v1/developer/keys", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 3. Rotate Key
    rotate_res = await client.post(
        f"/api/v1/developer/keys/{key_id}/rotate",
        json={"expires_in_days": 45},
        headers=headers,
    )
    assert rotate_res.status_code == 200
    rotated_data = rotate_res.json()
    assert rotated_data["id"] != key_id
    assert "raw_key" in rotated_data

    # 4. Revoke Key
    del_res = await client.delete(f"/api/v1/developer/keys/{rotated_data['id']}", headers=headers)
    assert del_res.status_code == 204

    # 5. GET /api/v1/developer/analytics
    analytics_res = await client.get("/api/v1/developer/analytics", headers=headers)
    assert analytics_res.status_code == 200
    assert "total_requests" in analytics_res.json()


@pytest.mark.asyncio
async def test_developer_integrations_and_plugins(client: AsyncClient, db_session):
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Integration Tester",
        email=f"integ_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"X-User-Id": str(user_id)}

    # 1. List integrations
    integ_res = await client.get("/api/v1/developer/integrations", headers=headers)
    assert integ_res.status_code == 200
    items = integ_res.json()["items"]
    assert len(items) >= 8

    # 2. Connect Gmail
    conn_res = await client.post(
        "/api/v1/developer/integrations/gmail/connect",
        json={"metadata": {"email": "test@gmail.com"}},
        headers=headers,
    )
    assert conn_res.status_code == 200
    assert conn_res.json()["status"] == "connected"

    # 3. Sync Gmail
    sync_res = await client.post(
        "/api/v1/developer/integrations/gmail/sync",
        headers=headers,
    )
    assert sync_res.status_code == 200
    assert sync_res.json()["success"] is True

    # 4. Disconnect Gmail
    disc_res = await client.post(
        "/api/v1/developer/integrations/gmail/disconnect",
        headers=headers,
    )
    assert disc_res.status_code == 200
    assert disc_res.json()["disconnected"] is True

    # 5. List plugins
    plugins_res = await client.get("/api/v1/developer/plugins", headers=headers)
    assert plugins_res.status_code == 200
    assert plugins_res.json()["total"] >= 3

    # 6. Register custom plugin
    plugin_payload = {
        "id": "slack_custom_bot",
        "name": "Custom Slack Bot",
        "version": "1.0.0",
        "description": "Custom slack bot integration",
        "capabilities": ["custom_analytics"],
    }
    reg_res = await client.post(
        "/api/v1/developer/plugins/register",
        json=plugin_payload,
        headers=headers,
    )
    assert reg_res.status_code == 200
    assert reg_res.json()["id"] == "slack_custom_bot"


@pytest.mark.asyncio
async def test_webhooks_api_lifecycle(client: AsyncClient, db_session):
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Webhook Tester",
        email=f"wh_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"X-User-Id": str(user_id)}

    # 1. Create Webhook
    wh_payload = {
        "endpoint": "https://httpbin.org/post",
        "events": ["job.matched", "application.created"],
        "enabled": True,
    }
    create_res = await client.post("/api/v1/webhooks", json=wh_payload, headers=headers)
    assert create_res.status_code == 201
    wh = create_res.json()
    assert wh["endpoint"] == "https://httpbin.org/post"
    assert "whsec_" in wh["secret"]
    wh_id = wh["id"]

    # 2. List Webhooks
    list_res = await client.get("/api/v1/webhooks", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 3. Get Webhook
    get_res = await client.get(f"/api/v1/webhooks/{wh_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == wh_id

    # 4. Patch Webhook
    patch_res = await client.patch(
        f"/api/v1/webhooks/{wh_id}",
        json={"enabled": False},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["enabled"] is False

    # 5. Test Webhook
    test_res = await client.post(
        f"/api/v1/webhooks/{wh_id}/test",
        json={"event": "job.matched"},
        headers=headers,
    )
    assert test_res.status_code == 200
    assert "signature" in test_res.json()

    # 6. List Deliveries
    deliv_res = await client.get(f"/api/v1/webhooks/{wh_id}/deliveries", headers=headers)
    assert deliv_res.status_code == 200
    assert deliv_res.json()["total"] >= 1

    # 7. Delete Webhook
    del_res = await client.delete(f"/api/v1/webhooks/{wh_id}", headers=headers)
    assert del_res.status_code == 204
