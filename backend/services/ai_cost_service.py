import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from core.exceptions import AIQuotaExceededException
from core.logging import get_logger

logger = get_logger("services.ai_cost")

# Pricing per million tokens (USD)
PRICING_TABLE = {
    "gemini-2.5-pro": {
        "input_per_m": 1.25,
        "output_per_m": 5.00,
    },
    "gemini-2.5-flash": {
        "input_per_m": 0.075,
        "output_per_m": 0.30,
    },
    "text-embedding-004": {
        "input_per_m": 0.025,
        "output_per_m": 0.025,
    },
}

DEFAULT_MONTHLY_BUDGET_USD = 50.0  # Default quota per candidate user


class AICostService:
    """
    Tracks and audits AI consumption metrics: tokens used, invocations count,
    cost calculations per model, and user quota management.
    """
    def __init__(self):
        # In-memory transaction log buffer (persisted or aggregated)
        self._records: List[Dict[str, Any]] = []
        # user_id -> monthly budget in USD
        self._user_budgets: Dict[str, float] = defaultdict(lambda: DEFAULT_MONTHLY_BUDGET_USD)

    @classmethod
    def calculate_cost(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculates USD cost using published model pricing tiers."""
        rates = PRICING_TABLE.get(model.lower(), PRICING_TABLE["gemini-2.5-pro"])
        input_cost = (prompt_tokens / 1_000_000) * rates["input_per_m"]
        output_cost = (completion_tokens / 1_000_000) * rates["output_per_m"]
        return round(input_cost + output_cost, 6)

    def record_usage(
        self,
        user_id: Optional[uuid.UUID],
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        operation: str = "orchestration",
    ) -> Dict[str, Any]:
        """
        Records an AI inference execution event with token counts and calculated cost.
        """
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        record_id = str(uuid.uuid4())

        record = {
            "id": record_id,
            "user_id": user_id,
            "model": model,
            "operation": operation,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
            "timestamp": datetime.now(timezone.utc),
        }
        self._records.append(record)

        # Telemetry hook for MonitoringService
        try:
            from services.monitoring_service import metrics_collector
            metrics_collector.record_ai_usage(total_tokens)
        except Exception:
            pass

        logger.info(
            f"[AI Cost] Recorded {operation} for user {user_id}: "
            f"{total_tokens} tokens (${cost:.6f}) using {model}"
        )
        return record

    def check_budget_limit(self, user_id: uuid.UUID) -> Tuple[bool, float, float]:
        """
        Verifies if candidate user is within their monthly AI consumption allowance.
        Returns: (is_within_budget: bool, current_spend_usd: float, budget_limit_usd: float)
        """
        limit = self._user_budgets[str(user_id)]
        user_records = [r for r in self._records if r.get("user_id") == user_id]
        total_spend = sum(r["cost_usd"] for r in user_records)

        is_allowed = total_spend < limit
        return is_allowed, round(total_spend, 4), limit

    def get_summary(
        self,
        user_id: Optional[uuid.UUID] = None,
        timeframe: str = "all",
    ) -> Dict[str, Any]:
        """
        Generates aggregated summary of AI consumption:
        - Total tokens, prompt tokens, completion tokens
        - Total cost USD and average cost per request
        - Breakdown by model
        - Breakdown by user
        """
        records = self._records
        if user_id:
            records = [r for r in records if r.get("user_id") == user_id]

        total_requests = len(records)
        total_prompt = sum(r["prompt_tokens"] for r in records)
        total_completion = sum(r["completion_tokens"] for r in records)
        total_tokens = total_prompt + total_completion
        total_cost = sum(r["cost_usd"] for r in records)
        avg_cost = round(total_cost / total_requests, 6) if total_requests > 0 else 0.0

        # Model breakdown
        model_groups = defaultdict(lambda: {"count": 0, "prompt": 0, "comp": 0, "tokens": 0, "cost": 0.0})
        for r in records:
            m = r["model"]
            model_groups[m]["count"] += 1
            model_groups[m]["prompt"] += r["prompt_tokens"]
            model_groups[m]["comp"] += r["completion_tokens"]
            model_groups[m]["tokens"] += r["total_tokens"]
            model_groups[m]["cost"] += r["cost_usd"]

        by_model = [
            {
                "model": m,
                "requests_count": data["count"],
                "prompt_tokens": data["prompt"],
                "completion_tokens": data["comp"],
                "total_tokens": data["tokens"],
                "total_cost_usd": round(data["cost"], 4),
                "avg_cost_per_request": round(data["cost"] / data["count"], 6) if data["count"] > 0 else 0.0,
            }
            for m, data in model_groups.items()
        ]

        # User breakdown
        user_groups = defaultdict(lambda: {"count": 0, "tokens": 0, "cost": 0.0})
        for r in records:
            u = r.get("user_id")
            if u:
                uid_str = str(u)
                user_groups[uid_str]["count"] += 1
                user_groups[uid_str]["tokens"] += r["total_tokens"]
                user_groups[uid_str]["cost"] += r["cost_usd"]

        by_user = [
            {
                "user_id": uuid.UUID(uid),
                "requests_count": data["count"],
                "total_tokens": data["tokens"],
                "total_cost_usd": round(data["cost"], 4),
                "budget_limit_usd": self._user_budgets[uid],
                "is_budget_exceeded": data["cost"] >= self._user_budgets[uid],
            }
            for uid, data in user_groups.items()
        ]

        return {
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_cost_usd": round(total_cost, 4),
            "avg_request_cost_usd": avg_cost,
            "by_model": by_model,
            "by_user": by_user,
            "timeframe": timeframe,
            "budget_alert_threshold_pct": 80.0,
        }


# Global AI cost service singleton
ai_cost_service = AICostService()
