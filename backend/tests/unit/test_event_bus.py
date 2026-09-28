import uuid
import pytest
from orchestration.event_bus import AgentEvent, EventBus


@pytest.mark.asyncio
async def test_event_bus_publish_and_subscribe():
    bus = EventBus(history_size=50)
    received_events = []

    async def on_resume_uploaded(event: AgentEvent):
        received_events.append(event)

    bus.subscribe("ResumeUploaded", on_resume_uploaded)

    test_user_id = uuid.uuid4()
    test_event = AgentEvent(
        event_name="ResumeUploaded",
        user_id=test_user_id,
        payload={"filename": "resume.pdf", "file_size": 102400},
    )

    await bus.publish(test_event)

    assert len(received_events) == 1
    assert received_events[0].event_name == "ResumeUploaded"
    assert received_events[0].payload["filename"] == "resume.pdf"
    assert received_events[0].user_id == test_user_id


@pytest.mark.asyncio
async def test_event_bus_wildcard_subscriber():
    bus = EventBus(history_size=50)
    wildcard_events = []

    async def wildcard_handler(event: AgentEvent):
        wildcard_events.append(event)

    bus.subscribe("*", wildcard_handler)

    await bus.publish(AgentEvent(event_name="MatchingCompleted", payload={"matches": 3}))
    await bus.publish(AgentEvent(event_name="ReportGenerated", payload={"report_id": "r1"}))

    assert len(wildcard_events) == 2


@pytest.mark.asyncio
async def test_event_bus_history_and_error_isolation():
    bus = EventBus(history_size=10)

    async def failing_subscriber(event: AgentEvent):
        raise RuntimeError("Subscriber crashed!")

    async def healthy_subscriber(event: AgentEvent):
        event.payload["healthy_received"] = True

    bus.subscribe("JobsDiscovered", failing_subscriber)
    bus.subscribe("JobsDiscovered", healthy_subscriber)

    payload = {"count": 10}
    event = AgentEvent(event_name="JobsDiscovered", payload=payload)
    await bus.publish(event)

    # Healthy subscriber still received event despite prior subscriber failure
    assert payload.get("healthy_received") is True

    # History contains the event
    history = bus.get_history(event_name="JobsDiscovered")
    assert len(history) == 1
    assert history[0].event_name == "JobsDiscovered"
