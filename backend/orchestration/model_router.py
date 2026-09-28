import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskComplexity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SpeedPreference(str, Enum):
    FASTEST = "FASTEST"
    BALANCED = "BALANCED"
    QUALITY = "QUALITY"


class CostPreference(str, Enum):
    LOWEST_COST = "LOWEST_COST"
    STANDARD = "STANDARD"
    MAX_ACCURACY = "MAX_ACCURACY"


class PrivacyLevel(str, Enum):
    CLOUD = "CLOUD"
    LOCAL_ONLY = "LOCAL_ONLY"


@dataclass
class ModelProfile:
    id: str
    name: str
    provider: str  # google, openai, anthropic, nvidia, ollama
    complexity_fit: List[TaskComplexity]
    latency_tier: str  # ultra_low (<1s), low (1-2s), moderate (2-4s), high (4-8s)
    cost_tier: str  # free, low, medium, high
    context_window: int
    strengths: List[str]
    is_local: bool = False


# Catalog of supported platform models
SUPPORTED_MODELS: Dict[str, ModelProfile] = {
    "gemini-2.5-pro": ModelProfile(
        id="gemini-2.5-pro",
        name="Google Gemini 2.5 Pro",
        provider="google",
        complexity_fit=[TaskComplexity.HIGH],
        latency_tier="moderate",
        cost_tier="medium",
        context_window=1000000,
        strengths=["Deep multi-step reasoning", "Complex resume tailoring", "Interview coaching"],
    ),
    "gemini-2.5-flash": ModelProfile(
        id="gemini-2.5-flash",
        name="Google Gemini 2.5 Flash",
        provider="google",
        complexity_fit=[TaskComplexity.LOW, TaskComplexity.MEDIUM],
        latency_tier="ultra_low",
        cost_tier="low",
        context_window=1000000,
        strengths=["Rapid skill extraction", "ATS keyword scoring", "Job classification"],
    ),
    "gpt-4o": ModelProfile(
        id="gpt-4o",
        name="OpenAI GPT-4o",
        provider="openai",
        complexity_fit=[TaskComplexity.HIGH],
        latency_tier="low",
        cost_tier="high",
        context_window=128000,
        strengths=["Conversational interview simulation", "Code assessment", "STAR critique"],
    ),
    "gpt-4o-mini": ModelProfile(
        id="gpt-4o-mini",
        name="OpenAI GPT-4o Mini",
        provider="openai",
        complexity_fit=[TaskComplexity.LOW, TaskComplexity.MEDIUM],
        latency_tier="ultra_low",
        cost_tier="low",
        context_window=128000,
        strengths=["High-throughput batch job filtering", "Contact parsing"],
    ),
    "claude-3-5-sonnet": ModelProfile(
        id="claude-3-5-sonnet",
        name="Anthropic Claude 3.5 Sonnet",
        provider="anthropic",
        complexity_fit=[TaskComplexity.HIGH],
        latency_tier="low",
        cost_tier="high",
        context_window=200000,
        strengths=["Exceptional prose & cover letter synthesis", "Nuanced reporting", "Recruiter communications"],
    ),
    "nemotron-70b": ModelProfile(
        id="nemotron-70b",
        name="NVIDIA Llama-3.1-Nemotron-70B-Instruct",
        provider="nvidia",
        complexity_fit=[TaskComplexity.MEDIUM, TaskComplexity.HIGH],
        latency_tier="moderate",
        cost_tier="medium",
        context_window=128000,
        strengths=["Structured synthetic data", "Enterprise recruitment benchmarking", "Domain reasoning"],
    ),
    "nvidia/nemotron-4-340b-instruct": ModelProfile(
        id="nvidia/nemotron-4-340b-instruct",
        name="NVIDIA Nemotron-4-340B-Instruct",
        provider="nvidia",
        complexity_fit=[TaskComplexity.HIGH],
        latency_tier="moderate",
        cost_tier="medium",
        context_window=128000,
        strengths=["Enterprise reasoning", "High complexity recruitment analytics"],
    ),
    "ollama-llama3.3": ModelProfile(
        id="ollama-llama3.3",
        name="Ollama Llama 3.3 (Local)",
        provider="ollama",
        complexity_fit=[TaskComplexity.LOW, TaskComplexity.MEDIUM],
        latency_tier="low",
        cost_tier="free",
        context_window=32768,
        strengths=["Air-gapped private parsing", "Zero API cost", "No data egress"],
        is_local=True,
    ),
    "llama3.1:8b": ModelProfile(
        id="llama3.1:8b",
        name="Ollama Llama 3.1 8B (Local)",
        provider="ollama",
        complexity_fit=[TaskComplexity.LOW, TaskComplexity.MEDIUM],
        latency_tier="low",
        cost_tier="free",
        context_window=32768,
        strengths=["Lightweight on-device parsing", "Zero API cost"],
        is_local=True,
    ),
}


class AIModelRouter:
    """
    Intelligent Model Router that dynamically routes tasks to the optimal LLM
    based on complexity, latency, cost constraints, privacy, and provider availability.
    """

    def __init__(self, default_fallback: str = "gemini-2.5-flash") -> None:
        self.default_fallback = default_fallback

    def route(
        self,
        task_type: str,
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
        speed_preference: SpeedPreference = SpeedPreference.BALANCED,
        cost_preference: CostPreference = CostPreference.STANDARD,
        privacy_level: PrivacyLevel = PrivacyLevel.CLOUD,
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate constraints and return selected model profile and rationale.
        """
        # 1. Check explicit override
        if model_override and model_override in SUPPORTED_MODELS:
            profile = SUPPORTED_MODELS[model_override]
            return {
                "selected_model": profile.id,
                "provider": profile.provider,
                "rationale": f"Explicit model override requested: {profile.name}",
                "estimated_cost_tier": profile.cost_tier,
                "context_window": profile.context_window,
            }

        # 2. Privacy constraint (e.g. local Ollama only)
        if privacy_level == PrivacyLevel.LOCAL_ONLY:
            local_profile = SUPPORTED_MODELS["ollama-llama3.3"]
            return {
                "selected_model": local_profile.id,
                "provider": local_profile.provider,
                "rationale": "Local-only privacy policy: Routed to on-premise Ollama instance without data egress.",
                "estimated_cost_tier": local_profile.cost_tier,
                "context_window": local_profile.context_window,
            }

        # 3. High Complexity / Deep Reasoning Tasks
        if complexity == TaskComplexity.HIGH or cost_preference == CostPreference.MAX_ACCURACY:
            if speed_preference == SpeedPreference.QUALITY and self._has_api_key("anthropic"):
                m = SUPPORTED_MODELS["claude-3-5-sonnet"]
                return {
                    "selected_model": m.id,
                    "provider": m.provider,
                    "rationale": "High complexity with quality priority routed to Claude 3.5 Sonnet.",
                    "estimated_cost_tier": m.cost_tier,
                    "context_window": m.context_window,
                }
            if self._has_api_key("openai") and task_type in ("interview_coaching", "interactive_evaluation"):
                m = SUPPORTED_MODELS["gpt-4o"]
                return {
                    "selected_model": m.id,
                    "provider": m.provider,
                    "rationale": "Conversational simulation routed to OpenAI GPT-4o.",
                    "estimated_cost_tier": m.cost_tier,
                    "context_window": m.context_window,
                }
            # Default enterprise deep reasoning: Gemini 2.5 Pro
            m = SUPPORTED_MODELS["gemini-2.5-pro"]
            return {
                "selected_model": m.id,
                "provider": m.provider,
                "rationale": "Complex reasoning and document synthesis routed to Google Gemini 2.5 Pro.",
                "estimated_cost_tier": m.cost_tier,
                "context_window": m.context_window,
            }

        # 4. Low Cost / Ultra Fast Tasks
        if speed_preference == SpeedPreference.FASTEST or cost_preference == CostPreference.LOWEST_COST:
            m = SUPPORTED_MODELS["gemini-2.5-flash"]
            return {
                "selected_model": m.id,
                "provider": m.provider,
                "rationale": "Speed and cost-efficiency optimized: routed to Google Gemini 2.5 Flash (<1s latency).",
                "estimated_cost_tier": m.cost_tier,
                "context_window": m.context_window,
            }

        # 5. Balanced default routing based on task type
        if task_type in ("resume_scoring", "ats_analysis", "job_ranking", "skill_matching"):
            m = SUPPORTED_MODELS["gemini-2.5-flash"]
            return {
                "selected_model": m.id,
                "provider": m.provider,
                "rationale": f"Structured extraction for {task_type} routed to Gemini 2.5 Flash.",
                "estimated_cost_tier": m.cost_tier,
                "context_window": m.context_window,
            }

        m = SUPPORTED_MODELS[self.default_fallback]
        return {
            "selected_model": m.id,
            "provider": m.provider,
            "rationale": f"Standard balanced tier routed to {m.name}.",
            "estimated_cost_tier": m.cost_tier,
            "context_window": m.context_window,
        }

    def _has_api_key(self, provider: str) -> bool:
        """Check if third-party provider API key is configured."""
        if provider == "openai":
            return bool(os.getenv("OPENAI_API_KEY"))
        elif provider == "anthropic":
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        elif provider == "nvidia":
            return bool(os.getenv("NVIDIA_API_KEY"))
        return False

    def list_models(self) -> List[Dict[str, Any]]:
        """Return all supported model profiles."""
        return [
            {
                "id": m.id,
                "model": m.id,
                "name": m.name,
                "provider": m.provider,
                "latency_tier": m.latency_tier,
                "cost_tier": m.cost_tier,
                "context_window": m.context_window,
                "strengths": m.strengths,
                "is_local": m.is_local,
            }
            for m in SUPPORTED_MODELS.values()
        ]

    def get_supported_models(self) -> List[Dict[str, Any]]:
        return self.list_models()


# Global Singleton Model Router
model_router = AIModelRouter()
