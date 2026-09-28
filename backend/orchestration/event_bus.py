import asyncio
import inspect
import logging
import time
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

EventHandler = Callable[[Any], Awaitable[None]]


@dataclass
class AgentEvent:
    event_name: str
    user_id: Optional[uuid.UUID] = None
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.user_id:
            d["user_id"] = str(self.user_id)
        d["iso_time"] = datetime.fromtimestamp(self.timestamp, timezone.utc).isoformat()
        return d


@dataclass
class ResumeUploadedEvent(AgentEvent):
    event_name: str = "ResumeUploaded"


@dataclass
class ResumeParsedEvent(AgentEvent):
    event_name: str = "ResumeParsed"


@dataclass
class JobsDiscoveredEvent(AgentEvent):
    event_name: str = "JobsDiscovered"


@dataclass
class MatchingCompletedEvent(AgentEvent):
    event_name: str = "MatchingCompleted"


@dataclass
class ReportGeneratedEvent(AgentEvent):
    event_name: str = "ReportGenerated"


@dataclass
class WorkflowStartedEvent(AgentEvent):
    event_name: str = "WorkflowStarted"


@dataclass
class WorkflowCompletedEvent(AgentEvent):
    event_name: str = "WorkflowCompleted"


@dataclass
class TaskCreatedEvent(AgentEvent):
    event_name: str = "TaskCreated"


@dataclass
class TaskCompletedEvent(AgentEvent):
    event_name: str = "TaskCompleted"


class EventBus:
    """
    Internal asynchronous Event Bus for orchestrating multi-agent workflows,
    decoupling service side-effects, and powering real-time observability.
    """

    def __init__(self, history_size: int = 100) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._history: deque[AgentEvent] = deque(maxlen=history_size)
        self._wildcard_subscribers: List[EventHandler] = []

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe an async handler to a specific event name or '*' for all events."""
        if event_name == "*":
            if handler not in self._wildcard_subscribers:
                self._wildcard_subscribers.append(handler)
        else:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            if handler not in self._subscribers[event_name]:
                self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """Remove a subscriber handler."""
        if event_name == "*" and handler in self._wildcard_subscribers:
            self._wildcard_subscribers.remove(handler)
        elif event_name in self._subscribers and handler in self._subscribers[event_name]:
            self._subscribers[event_name].remove(handler)

    async def publish(self, event: AgentEvent) -> None:
        """
        Publish an event to all registered subscribers asynchronously.
        Executes handlers concurrently with error isolation.
        """
        self._history.append(event)
        handlers = list(self._subscribers.get(event.event_name, [])) + list(self._wildcard_subscribers)

        if not handlers:
            return

        tasks = []
        for h in handlers:
            tasks.append(self._invoke_handler(h, event))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _invoke_handler(self, handler: EventHandler, event: AgentEvent) -> None:
        try:
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"[EventBus] Error executing subscriber {handler.__name__} on {event.event_name}: {e}", exc_info=True)

    def get_history(self, event_name: Optional[str] = None, limit: int = 50) -> List[AgentEvent]:
        """Return recently recorded events for telemetry and debugging, optionally filtered by event_name."""
        events = list(self._history)
        if event_name:
            events = [e for e in events if e.event_name == event_name]
        return events[-limit:]

    def clear(self) -> None:
        """Clear all subscribers and history (useful for hermetic unit testing)."""
        self._subscribers.clear()
        self._wildcard_subscribers.clear()
        self._history.clear()


# Global Singleton Event Bus
event_bus = EventBus()
