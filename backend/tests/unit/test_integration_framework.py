import uuid
from datetime import datetime, timezone
import pytest
from integrations.email_providers import GmailProvider, OutlookProvider
from integrations.calendar_providers import GoogleCalendarProvider, OutlookCalendarProvider
from integrations.storage_providers import GoogleDriveProvider, DropboxProvider, OneDriveProvider
from integrations.slack_provider import SlackProvider
from integrations.manager import IntegrationManager


@pytest.mark.asyncio
async def test_email_providers():
    gmail = GmailProvider()
    conn_meta = await gmail.connect({"email": "test@gmail.com"})
    assert conn_meta["email"] == "test@gmail.com"
    assert await gmail.health_check(conn_meta) is True

    # Test storing email
    store_res = await gmail.store_application_email(
        connection_metadata=conn_meta,
        application_id="app-123",
        recipient="jobs@stripe.com",
        subject="Application for Staff Engineer",
        body="Hello...",
    )
    assert store_res["stored"] is True
    assert "gmail" in store_res["message_id"]

    # Test tracking replies
    replies = await gmail.track_recruiter_replies(conn_meta, ["recruiter@stripe.com"])
    assert len(replies) > 0
    assert replies[0]["from"] == "recruiter@stripe.com"

    # Test Outlook
    outlook = OutlookProvider()
    ms_conn = await outlook.connect({"email": "test@outlook.com"})
    assert await outlook.health_check(ms_conn) is True


@pytest.mark.asyncio
async def test_calendar_providers():
    gcal = GoogleCalendarProvider()
    conn_meta = await gcal.connect({"calendar_id": "primary"})
    now = datetime.now(timezone.utc)

    # Schedule interview
    event = await gcal.schedule_interview(
        connection_metadata=conn_meta,
        title="Technical Architectural Review",
        start_time=now,
        duration_minutes=60,
        attendees=["candidate@example.com", "interviewer@stripe.com"],
        meeting_link="https://meet.google.com/test-meet",
    )
    assert event["status"] == "confirmed"
    assert "https://meet.google.com" in event["meeting_link"]

    # Sync events
    events = await gcal.sync_events(conn_meta)
    assert len(events) > 0

    # Test Outlook Calendar
    ms_cal = OutlookCalendarProvider()
    ms_conn = await ms_cal.connect({})
    assert await ms_cal.health_check(ms_conn) is True


@pytest.mark.asyncio
async def test_storage_providers():
    gdrive = GoogleDriveProvider()
    conn_meta = await gdrive.connect({"root_folder": "AI Copilot"})

    # Backup resume
    content = b"PDF resume binary data"
    backup = await gdrive.backup_resume(
        connection_metadata=conn_meta,
        filename="Alex_Chen_Resume.pdf",
        content=content,
    )
    assert backup["size_bytes"] == len(content)
    assert "drive.google.com" in backup["web_view_link"]

    # Dropbox & OneDrive
    dropbox = DropboxProvider()
    db_conn = await dropbox.connect({})
    db_res = await dropbox.export_report(db_conn, "report.pdf", content)
    assert db_res["size_bytes"] == len(content)

    onedrive = OneDriveProvider()
    od_conn = await onedrive.connect({})
    assert await onedrive.health_check(od_conn) is True


@pytest.mark.asyncio
async def test_slack_provider():
    slack = SlackProvider()
    conn_meta = await slack.connect({"channel": "#alerts"})
    assert await slack.health_check(conn_meta) is True

    notif = await slack.send_application_notification(
        connection_metadata=conn_meta,
        job_title="Staff Engineer",
        company="Stripe",
        status="Interviewing",
    )
    assert notif["sent"] is True
    assert "#alerts" in notif["channel"]


@pytest.mark.asyncio
async def test_integration_manager_lifecycle(db_session):
    manager = IntegrationManager(db_session)
    user_id = uuid.uuid4()

    # 1. List available integrations
    integrations = await manager.list_integrations_for_user(user_id)
    assert len(integrations) >= 8
    gmail_info = next(i for i in integrations if i["provider"] == "gmail")
    assert gmail_info["is_connected"] is False

    # 2. Connect Gmail
    conn = await manager.connect_integration(
        user_id=user_id,
        provider_id="gmail",
        auth_payload={"email": "candidate@gmail.com"},
    )
    assert conn.status == "connected"

    # 3. Verify connected status
    integrations_after = await manager.list_integrations_for_user(user_id)
    gmail_updated = next(i for i in integrations_after if i["provider"] == "gmail")
    assert gmail_updated["is_connected"] is True

    # 4. Trigger Sync
    sync_res = await manager.sync_integration(user_id=user_id, provider_id="gmail")
    assert sync_res["success"] is True

    # 5. Disconnect
    disconnected = await manager.disconnect_integration(user_id=user_id, provider_id="gmail")
    assert disconnected is True
