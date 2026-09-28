"""
AI Orchestrator with 3-Attempt Adaptive Fallback and Telemetry.
Attempt 1: Gemini 2.5 Pro
Attempt 2: Gemini 2.5 Pro
Attempt 3: Gemini 2.5 Flash
"""
import time
from typing import Any, Dict, List, Optional, Tuple
from core.ai.base import AIProvider
from core.ai.gemini import GeminiFlashProvider, GeminiProProvider
from core.exceptions import AIServiceException
from core.logging import get_logger

logger = get_logger("ai.orchestrator")


class AIOrchestrator:
    """
    Coordinates multi-attempt AI inference with primary-to-fallback failover,
    latency instrumentation, and audit logging.
    """

    def __init__(
        self,
        pro_provider: Optional[AIProvider] = None,
        flash_provider: Optional[AIProvider] = None,
    ):
        self.pro_provider = pro_provider or GeminiProProvider()
        self.flash_provider = flash_provider or GeminiFlashProvider()

    async def execute_with_fallback(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Executes inference across the 3-attempt lifecycle:
        1. Attempt 1: Gemini Pro
        2. Attempt 2: Gemini Pro
        3. Attempt 3: Gemini Flash (Fallback)

        Returns:
            Tuple of (raw_json_string, execution_telemetry_dict)
        Raises:
            AIServiceException if all 3 attempts fail.
        """
        attempts_plan = [
            {"attempt": 1, "name": "Primary Attempt 1", "provider": self.pro_provider},
            {"attempt": 2, "name": "Primary Attempt 2 (Retry)", "provider": self.pro_provider},
            {"attempt": 3, "name": "Fallback Attempt 3 (Flash)", "provider": self.flash_provider},
        ]

        attempt_history: List[Dict[str, Any]] = []
        overall_start = time.perf_counter()

        for step in attempts_plan:
            attempt_num = step["attempt"]
            step_name = step["name"]
            provider: AIProvider = step["provider"]
            model = provider.model_name

            logger.info(
                f"[AI Orchestrator] Starting {step_name} using {model}",
                extra={"attempt": attempt_num, "model": model},
            )

            step_start = time.perf_counter()
            try:
                raw_json = await provider.generate_json(
                    prompt=prompt,
                    system_instruction=system_instruction,
                )
                duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
                total_duration_ms = round((time.perf_counter() - overall_start) * 1000, 2)

                prompt_tokens = max(1, len(prompt) // 4)
                completion_tokens = max(1, len(raw_json) // 4)

                cost_telemetry = {}
                try:
                    from services.ai_cost_service import ai_cost_service
                    cost_record = ai_cost_service.record_usage(
                        user_id=None,
                        model=model,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        operation="inference_orchestration",
                    )
                    cost_telemetry = {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                        "cost_usd": cost_record["cost_usd"],
                    }
                except Exception:
                    pass

                telemetry = {
                    "success": True,
                    "attempt": attempt_num,
                    "model_used": model,
                    "duration_ms": duration_ms,
                    "total_duration_ms": total_duration_ms,
                    "tokens": cost_telemetry,
                    "history": attempt_history + [{
                        "attempt": attempt_num,
                        "model": model,
                        "status": "SUCCESS",
                        "duration_ms": duration_ms,
                    }],
                }

                logger.info(
                    f"[AI Orchestrator] {step_name} succeeded in {duration_ms}ms",
                    extra=telemetry,
                )
                return raw_json, telemetry

            except Exception as exc:
                duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
                error_msg = str(exc)
                logger.warning(
                    f"[AI Orchestrator] {step_name} failed ({duration_ms}ms): {error_msg}",
                    extra={
                        "attempt": attempt_num,
                        "model": model,
                        "duration_ms": duration_ms,
                        "error": error_msg,
                    },
                )
                attempt_history.append({
                    "attempt": attempt_num,
                    "model": model,
                    "status": "FAILED",
                    "duration_ms": duration_ms,
                    "error": error_msg,
                })

        # All 3 attempts failed
        total_duration_ms = round((time.perf_counter() - overall_start) * 1000, 2)
        logger.error(
            f"[AI Orchestrator] Exhausted all 3 attempts after {total_duration_ms}ms.",
            extra={"history": attempt_history, "total_duration_ms": total_duration_ms},
        )

        raise AIServiceException(
            message="Resume Intelligence Engine failed after 3 attempts (Gemini Pro x2, Gemini Flash x1).",
            details={
                "attempts_total": 3,
                "total_duration_ms": total_duration_ms,
                "history": attempt_history,
            },
        )
