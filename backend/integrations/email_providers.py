from abc import abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from integrations.base import IntegrationProvider


class EmailProvider(IntegrationProvider):
    """
    Base email integration providing recruiter thread tracking, email archival, and invite ingestion.
    """
    @property
    def category(self) -> str:
        return "email"

    @property
    def capabilities(self) -> List[str]:
        return ["store_application_emails", "track_recruiter_replies", "import_interview_invitations"]

    @abstractmethod
    async def store_application_email(
        self,
        connection_metadata: Dict[str, Any],
        application_id: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        """Archives an outbound job application email to the user's mail sent box or label."""
        pass

    @abstractmethod
    async def track_recruiter_replies(
        self,
        connection_metadata: Dict[str, Any],
        recruiter_emails: List[str],
        since_timestamp: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Scans inbox for new replies from recognized recruiters."""
        pass

    @abstractmethod
    async def import_interview_invitations(
        self,
        connection_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Parses incoming calendar invites and recruiter scheduling links."""
        pass


class GmailProvider(EmailProvider):
    @property
    def provider_id(self) -> str:
        return "gmail"

    @property
    def display_name(self) -> str:
        return "Gmail / Google Workspace"

    @property
    def description(self) -> str:
        return "Synchronize application threads, track recruiter replies, and auto-detect interview invitations."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        email = auth_payload.get("email") or "user@gmail.com"
        return {
            "email": email,
            "access_token": auth_payload.get("access_token", "ya29.mock_gmail_token"),
            "refresh_token": auth_payload.get("refresh_token", "1//mock_refresh"),
            "history_id": "1001",
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def store_application_email(
        self,
        connection_metadata: Dict[str, Any],
        application_id: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        return {
            "provider": self.provider_id,
            "message_id": f"msg_gmail_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "application_id": application_id,
            "recipient": recipient,
            "subject": subject,
            "stored": True,
        }

    async def track_recruiter_replies(
        self,
        connection_metadata: Dict[str, Any],
        recruiter_emails: List[str],
        since_timestamp: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        replies = []
        for idx, email in enumerate(recruiter_emails[:3]):
            replies.append({
                "thread_id": f"th_gmail_{idx}",
                "from": email,
                "subject": f"Re: Application Follow-up ({email})",
                "snippet": "Thanks for reaching out! We'd love to schedule a technical chat this week.",
                "received_at": datetime.now(timezone.utc).isoformat(),
            })
        return replies

    async def import_interview_invitations(
        self,
        connection_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        return [
            {
                "invite_id": "inv_gmail_01",
                "organizer": "recruiting@techcorp.com",
                "summary": "Technical Screen with AI Copilot Team",
                "scheduled_time": datetime.now(timezone.utc).isoformat(),
                "meeting_link": "https://meet.google.com/abc-defg-hij",
            }
        ]


class OutlookProvider(EmailProvider):
    @property
    def provider_id(self) -> str:
        return "outlook"

    @property
    def display_name(self) -> str:
        return "Microsoft Outlook / Office 365"

    @property
    def description(self) -> str:
        return "Ingest Microsoft 365 recruiter correspondence, store sent resumes, and detect meeting requests."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        email = auth_payload.get("email") or "user@outlook.com"
        return {
            "email": email,
            "access_token": auth_payload.get("access_token", "mock_outlook_token"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def store_application_email(
        self,
        connection_metadata: Dict[str, Any],
        application_id: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> Dict[str, Any]:
        return {
            "provider": self.provider_id,
            "message_id": f"msg_ms_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "application_id": application_id,
            "recipient": recipient,
            "subject": subject,
            "stored": True,
        }

    async def track_recruiter_replies(
        self,
        connection_metadata: Dict[str, Any],
        recruiter_emails: List[str],
        since_timestamp: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "thread_id": "th_ms_01",
                "from": recruiter_emails[0] if recruiter_emails else "recruiter@enterprise.com",
                "subject": "Interview Invitation",
                "snippet": "We have reviewed your profile and want to invite you to an interview.",
                "received_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    async def import_interview_invitations(
        self,
        connection_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        return [
            {
                "invite_id": "inv_ms_01",
                "organizer": "talent@enterprise.com",
                "summary": "Round 1 Coding Interview",
                "scheduled_time": datetime.now(timezone.utc).isoformat(),
                "meeting_link": "https://teams.microsoft.com/l/meetup-join/123",
            }
        ]
