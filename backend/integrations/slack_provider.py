from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from integrations.base import IntegrationProvider


class SlackProvider(IntegrationProvider):
    """
    Slack integration for real-time application tracking alerts, interview reminders, and match digests.
    """
    @property
    def provider_id(self) -> str:
        return "slack"

    @property
    def category(self) -> str:
        return "notification"

    @property
    def display_name(self) -> str:
        return "Slack"

    @property
    def description(self) -> str:
        return "Receive instant application status changes, interview alerts, and AI job match notifications in Slack channels."

    @property
    def capabilities(self) -> List[str]:
        return ["application_notifications", "interview_reminders", "match_alerts"]

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "channel": auth_payload.get("channel", "#job-search"),
            "webhook_url": auth_payload.get("webhook_url", "https://hooks.slack.com/services/mock/token"),
            "team_name": auth_payload.get("team_name", "Career Copilot Workspace"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("webhook_url"))

    async def send_application_notification(
        self,
        connection_metadata: Dict[str, Any],
        job_title: str,
        company: str,
        status: str,
    ) -> Dict[str, Any]:
        return {
            "sent": True,
            "provider": self.provider_id,
            "channel": connection_metadata.get("channel", "#job-search"),
            "message": f"🚀 Application status updated: *{job_title}* at *{company}* is now *{status}*.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def send_interview_reminder(
        self,
        connection_metadata: Dict[str, Any],
        interview_title: str,
        time_str: str,
        meeting_link: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "sent": True,
            "provider": self.provider_id,
            "channel": connection_metadata.get("channel", "#job-search"),
            "message": f"📅 Interview Reminder: *{interview_title}* scheduled for *{time_str}*! Link: {meeting_link or 'N/A'}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
