import uuid
import pytest
from services.ai_cost_service import AICostService


@pytest.mark.asyncio
async def test_ai_cost_service_pricing_calculation():
    # 1,000,000 prompt tokens + 1,000,000 completion tokens on gemini-2.5-pro = $1.25 + $5.00 = $6.25
    cost = AICostService.calculate_cost("gemini-2.5-pro", 1_000_000, 1_000_000)
    assert cost == 6.25

    # 1,000,000 prompt + 1,000,000 completion on gemini-2.5-flash = $0.075 + $0.30 = $0.375
    cost_flash = AICostService.calculate_cost("gemini-2.5-flash", 1_000_000, 1_000_000)
    assert cost_flash == 0.375


@pytest.mark.asyncio
async def test_ai_cost_service_record_and_summary():
    service = AICostService()
    user_id = uuid.uuid4()

    record1 = service.record_usage(
        user_id=user_id,
        model="gemini-2.5-pro",
        prompt_tokens=1000,
        completion_tokens=500,
        operation="resume_tailoring",
    )
    assert record1["total_tokens"] == 1500
    assert record1["cost_usd"] > 0

    record2 = service.record_usage(
        user_id=user_id,
        model="gemini-2.5-flash",
        prompt_tokens=2000,
        completion_tokens=1000,
        operation="interview_questions",
    )
    assert record2["total_tokens"] == 3000

    summary = service.get_summary(user_id=user_id)
    assert summary["total_requests"] == 2
    assert summary["total_tokens"] == 4500
    assert len(summary["by_model"]) == 2

    # Check user budget
    is_ok, spend, limit = service.check_budget_limit(user_id)
    assert is_ok is True
    assert spend > 0
    assert limit == 50.0
