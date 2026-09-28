from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from integrations.base import IntegrationProvider


class CalendarProvider(IntegrationProvider):
    """
    Base calendar integration for interview scheduling and timeline synchronization.
    """
    @property
    def category(self) -> str:
        return "calendar"

    @property
    def capabilities(self) -> List[str]:
        return ["interview_scheduling", "event_synchronization"]

    @abstractmethod
    async def schedule_interview(
        self,
        connection_metadata: Dict[str, Any],
        title: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: List[str],
        meeting_link: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates an interview event on the candidate's external calendar."""
        pass

    @abstractmethod
    async def sync_events(
        self,
        connection_metadata: Dict[str, Any],
        since_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Pulls upcoming scheduled interviews and busy slots."""
        pass


class GoogleCalendarProvider(CalendarProvider):
    @property
    def provider_id(self) -> str:
        return "google_calendar"

    @property
    def display_name(self) -> str:
        return "Google Calendar"

    @property
    def description(self) -> str:
        return "Automatically block interview preparation sessions, sync recruiter interviews, and attach Google Meet links."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "calendar_id": auth_payload.get("calendar_id", "primary"),
            "access_token": auth_payload.get("access_token", "ya29.mock_gcal_token"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def schedule_interview(
        self,
        connection_metadata: Dict[str, Any],
        title: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: List[str],
        meeting_link: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        end_time = start_time + timedelta(minutes=duration_minutes)
        event_id = f"gcal_evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "provider": self.provider_id,
            "event_id": event_id,
            "calendar_id": connection_metadata.get("calendar_id", "primary"),
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "attendees": attendees,
            "meeting_link": meeting_link or f"https://meet.google.com/{event_id[-9:]}",
            "html_link": f"https://calendar.google.com/event?eid={event_id}",
            "status": "confirmed",
        }

    async def sync_events(
        self,
        connection_metadata: Dict[str, Any],
        since_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "event_id": "gcal_sync_01",
                "title": "System Design Interview (Mock or Live)",
                "start": (now + timedelta(days=2)).isoformat(),
                "end": (now + timedelta(days=2, hours=1)).isoformat(),
                "meeting_link": "https://meet.google.com/xyz-uvw-rst",
            }
        ]


class OutlookCalendarProvider(CalendarProvider):
    @property
    def provider_id(self) -> str:
        return "outlook_calendar"

    @property
    def display_name(self) -> str:
        return "Outlook Calendar"

    @property
    def description(self) -> str:
        return "Schedule interviews and sync availability across Microsoft 365 and Teams."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "calendar_id": auth_payload.get("calendar_id", "default"),
            "access_token": auth_payload.get("access_token", "mock_outlook_cal_token"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def schedule_interview(
        self,
        connection_metadata: Dict[str, Any],
        title: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: List[str],
        meeting_link: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        end_time = start_time + timedelta(minutes=duration_minutes)
        event_id = f"ms_cal_evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "provider": self.provider_id,
            "event_id": event_id,
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "attendees": attendees,
            "meeting_link": meeting_link or "https://teams.microsoft.com/l/meetup-join/sample",
            "status": "confirmed",
        }

    async def sync_events(
        self,
        connection_metadata: Dict[str, Any],
        since_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "event_id": "ms_sync_01",
                "title": "Hiring Manager Behavioral Interview",
                "start": (now + timedelta(days=3)).isoformat(),
                "end": (now + timedelta(days=3, minutes=45)).isoformat(),
                "meeting_link": "https://teams.microsoft.com/l/meetup-join/sample",
            }
        ]
