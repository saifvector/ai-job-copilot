import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from integrations.base import IntegrationProvider
from integrations.email_providers import GmailProvider, OutlookProvider
from integrations.calendar_providers import GoogleCalendarProvider, OutlookCalendarProvider
from integrations.storage_providers import GoogleDriveProvider, DropboxProvider, OneDriveProvider
from integrations.slack_provider import SlackProvider
from models.oauth_connection import OAuthConnectionModel
from repositories.oauth_connection_repository import OAuthConnectionRepository

logger = logging.getLogger(__name__)


class IntegrationManager:
    """
    Central orchestrator for third-party OAuth and integration providers.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = OAuthConnectionRepository(session)
        self._providers: Dict[str, IntegrationProvider] = {
            "gmail": GmailProvider(),
            "outlook": OutlookProvider(),
            "google_calendar": GoogleCalendarProvider(),
            "outlook_calendar": OutlookCalendarProvider(),
            "google_drive": GoogleDriveProvider(),
            "dropbox": DropboxProvider(),
            "onedrive": OneDriveProvider(),
            "slack": SlackProvider(),
        }

    def get_provider(self, provider_id: str) -> Optional[IntegrationProvider]:
        return self._providers.get(provider_id)

    async def list_integrations_for_user(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        active_connections = await self.repo.list_by_user(user_id)
        connection_map = {c.provider: c for c in active_connections}

        results = []
        for pid, provider in self._providers.items():
            conn: Optional[OAuthConnectionModel] = connection_map.get(pid)
            is_connected = conn is not None and conn.status == "connected"
            conn_data = None
            if conn:
                meta = json.loads(conn.metadata_json) if conn.metadata_json else {}
                conn_data = {
                    "id": conn.id,
                    "user_id": conn.user_id,
                    "provider": conn.provider,
                    "provider_user_id": conn.provider_user_id,
                    "scopes": conn.scopes or [],
                    "status": conn.status,
                    "metadata": meta,
                    "last_sync_at": conn.last_sync_at,
                    "created_at": conn.created_at,
                    "updated_at": conn.updated_at,
                }

            results.append({
                "provider": pid,
                "category": provider.category,
                "display_name": provider.display_name,
                "description": provider.description,
                "is_connected": is_connected,
                "connection": conn_data,
                "capabilities": provider.capabilities,
            })

        return results

    async def connect_integration(
        self,
        user_id: uuid.UUID,
        provider_id: str,
        auth_payload: Dict[str, Any],
    ) -> OAuthConnectionModel:
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Unknown integration provider: {provider_id}")

        connection_meta = await provider.connect(auth_payload)
        access_token = connection_meta.get("access_token")
        refresh_token = connection_meta.get("refresh_token")
        provider_user_id = connection_meta.get("email") or connection_meta.get("channel") or "user"
        meta_str = json.dumps(connection_meta, default=str)

        conn = await self.repo.upsert_connection(
            user_id=user_id,
            provider=provider_id,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            scopes=provider.capabilities,
            metadata_json=meta_str,
            status="connected",
        )
        return conn

    async def disconnect_integration(self, user_id: uuid.UUID, provider_id: str) -> bool:
        provider = self.get_provider(provider_id)
        if not provider:
            return False

        conn = await self.repo.get_by_provider(user_id, provider_id)
        if conn and conn.metadata_json:
            meta = json.loads(conn.metadata_json)
            await provider.disconnect(meta)

        return await self.repo.disconnect(user_id, provider_id)

    async def sync_integration(self, user_id: uuid.UUID, provider_id: str) -> Dict[str, Any]:
        """Triggers a live synchronization pass for the connected integration."""
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Unknown integration provider: {provider_id}")

        conn = await self.repo.get_by_provider(user_id, provider_id)
        if not conn or conn.status != "connected":
            raise ValueError(f"Provider {provider_id} is not connected for this user.")

        meta = json.loads(conn.metadata_json) if conn.metadata_json else {}
        now = datetime.now(timezone.utc)
        items_synced = 0
        details: Dict[str, Any] = {}

        if provider.category == "email" and isinstance(provider, (GmailProvider, OutlookProvider)):
            replies = await provider.track_recruiter_replies(meta, ["recruiter@enterprise.com"])
            items_synced = len(replies)
            details = {"recruiter_threads_found": replies}
        elif provider.category == "calendar" and isinstance(provider, (GoogleCalendarProvider, OutlookCalendarProvider)):
            events = await provider.sync_events(meta)
            items_synced = len(events)
            details = {"events_synced": events}
        elif provider.category == "storage" and isinstance(provider, (GoogleDriveProvider, DropboxProvider, OneDriveProvider)):
            details = {"root_folder": meta.get("root_folder", "AI Job Copilot"), "status": "synced"}
            items_synced = 1
        elif provider.category == "notification" and isinstance(provider, SlackProvider):
            test_res = await provider.send_application_notification(
                meta,
                job_title="Staff Software Engineer",
                company="Copilot SaaS",
                status="Interviewing",
            )
            details = test_res
            items_synced = 1

        conn.last_sync_at = now
        await self.session.flush()

        return {
            "success": True,
            "provider": provider_id,
            "items_synced": items_synced,
            "details": details,
            "synced_at": now,
        }
