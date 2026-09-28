import json
import pytest
from unittest.mock import AsyncMock
from core.ai.base import AIProvider
from core.ai.gemini import clean_json_response
from core.ai.orchestrator import AIOrchestrator
from core.exceptions import AIServiceException


class MockProvider(AIProvider):
    def __init__(self, name: str, responses: list):
        self._name = name
        self._responses = list(responses)
        self.call_count = 0

    @property
    def model_name(self) -> str:
        return self._name

    async def generate_json(self, prompt: str, system_instruction: str = None) -> str:
        self.call_count += 1
        if not self._responses:
            raise AIServiceException(f"{self._name} ran out of responses")
        outcome = self._responses.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_clean_json_response():
    markdown_wrapped = "```json\n{\"skills\": [\"Python\", \"FastAPI\"]}\n```"
    assert clean_json_response(markdown_wrapped) == "{\"skills\": [\"Python\", \"FastAPI\"]}"

    bare_wrapped = "```\n{\"name\": \"Alex\"}\n```"
    assert clean_json_response(bare_wrapped) == "{\"name\": \"Alex\"}"

    plain = "{\"name\": \"Alex Chen\"}"
    assert clean_json_response(plain) == "{\"name\": \"Alex Chen\"}"


@pytest.mark.asyncio
async def test_orchestrator_attempt_1_success():
    expected_json = json.dumps({"name": "Alex Chen", "skills": []})
    pro = MockProvider("gemini-2.5-pro", [expected_json])
    flash = MockProvider("gemini-2.5-flash", [])

    orchestrator = AIOrchestrator(pro_provider=pro, flash_provider=flash)
    result, telemetry = await orchestrator.execute_with_fallback("resume text")

    assert result == expected_json
    assert telemetry["attempt"] == 1
    assert telemetry["model_used"] == "gemini-2.5-pro"
    assert pro.call_count == 1
    assert flash.call_count == 0


@pytest.mark.asyncio
async def test_orchestrator_attempt_2_retry_success():
    expected_json = json.dumps({"name": "Alex Chen", "skills": []})
    # Attempt 1 fails with rate limit error, Attempt 2 succeeds
    pro = MockProvider("gemini-2.5-pro", [Exception("429 Resource Exhausted"), expected_json])
    flash = MockProvider("gemini-2.5-flash", [])

    orchestrator = AIOrchestrator(pro_provider=pro, flash_provider=flash)
    result, telemetry = await orchestrator.execute_with_fallback("resume text")

    assert result == expected_json
    assert telemetry["attempt"] == 2
    assert telemetry["model_used"] == "gemini-2.5-pro"
    assert pro.call_count == 2
    assert flash.call_count == 0


@pytest.mark.asyncio
async def test_orchestrator_attempt_3_flash_fallback_success():
    expected_json = json.dumps({"name": "Alex Chen", "skills": []})
    # Attempt 1 & 2 fail on Pro, Attempt 3 succeeds on Flash
    pro = MockProvider("gemini-2.5-pro", [Exception("503 Service Unavailable"), Exception("500 Internal Error")])
    flash = MockProvider("gemini-2.5-flash", [expected_json])

    orchestrator = AIOrchestrator(pro_provider=pro, flash_provider=flash)
    result, telemetry = await orchestrator.execute_with_fallback("resume text")

    assert result == expected_json
    assert telemetry["attempt"] == 3
    assert telemetry["model_used"] == "gemini-2.5-flash"
    assert pro.call_count == 2
    assert flash.call_count == 1


@pytest.mark.asyncio
async def test_orchestrator_all_attempts_fail_raises_ai_exception():
    pro = MockProvider("gemini-2.5-pro", [Exception("Fail 1"), Exception("Fail 2")])
    flash = MockProvider("gemini-2.5-flash", [Exception("Fail 3")])

    orchestrator = AIOrchestrator(pro_provider=pro, flash_provider=flash)

    with pytest.raises(AIServiceException) as exc_info:
        await orchestrator.execute_with_fallback("resume text")

    assert "Resume Intelligence Engine failed after 3 attempts" in str(exc_info.value)
    assert exc_info.value.details["attempts_total"] == 3
    assert len(exc_info.value.details["history"]) == 3
    assert pro.call_count == 2
    assert flash.call_count == 1
