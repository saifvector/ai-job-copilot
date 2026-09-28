import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AICostRecord(BaseModel):
    """Individual AI invocation token usage record."""
    id: str
    user_id: Optional[uuid.UUID] = None
    model: str
    operation: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime


class ModelUsageBreakdown(BaseModel):
    """Aggregate token usage and cost for a specific model."""
    model: str
    requests_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    total_cost_usd: float
    avg_cost_per_request: float


class UserCostBreakdown(BaseModel):
    """Aggregate token usage and cost for a specific user."""
    user_id: uuid.UUID
    requests_count: int
    total_tokens: int
    total_cost_usd: float
    budget_limit_usd: Optional[float] = None
    is_budget_exceeded: bool = False


class AICostSummaryResponse(BaseModel):
    """Global or scoped summary of AI consumption and cost."""
    total_requests: int
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: float
    avg_request_cost_usd: float
    by_model: List[ModelUsageBreakdown]
    by_user: List[UserCostBreakdown]
    timeframe: str
    budget_alert_threshold_pct: float
