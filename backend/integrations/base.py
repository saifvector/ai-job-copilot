from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IntegrationProvider(ABC):
    """
    Abstract base class for third-party platform integrations.
    Provides standard lifecycle contracts for authentication, synchronization, and telemetry.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Machine identifier (e.g. 'gmail', 'google_calendar', 'google_drive', 'slack')."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category: 'email', 'calendar', 'storage', 'notification'."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short overview of provider features."""
        pass

    @property
    def capabilities(self) -> List[str]:
        """List of supported functional capabilities."""
        return []

    @abstractmethod
    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validates credentials/token and returns connection metadata."""
        pass

    @abstractmethod
    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        """Revokes external authorization tokens."""
        pass

    @abstractmethod
    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        """Validates if external API credentials remain active."""
        pass
