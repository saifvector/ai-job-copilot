import pytest
from orchestration.model_router import model_router


def test_model_router_complexity_routing():
    # High complexity task
    routed_high = model_router.route(
        task_type="deep_code_review",
        complexity="HIGH",
    )
    assert routed_high["selected_model"] in ["gemini-2.5-pro", "claude-3-5-sonnet", "gpt-4o", "gemini-2.5-flash"]
    assert "rationale" in routed_high

    # Low complexity task
    routed_low = model_router.route(
        task_type="keyword_extraction",
        complexity="LOW",
        speed_preference="FASTEST",
    )
    assert routed_low["selected_model"] in ["gemini-2.5-flash", "gpt-4o-mini", "llama3.1:8b"]


def test_model_router_privacy_local_only():
    routed = model_router.route(
        task_type="sensitive_resume_analysis",
        privacy_level="LOCAL_ONLY",
    )
    assert routed["provider"] == "ollama"
    assert routed["selected_model"] in ["ollama-llama3.3", "llama3.1:8b"]


def test_model_router_override():
    routed = model_router.route(
        task_type="standard_matching",
        model_override="claude-3-5-sonnet",
    )
    assert routed["selected_model"] == "claude-3-5-sonnet"
    assert routed["provider"] == "anthropic"


def test_model_router_supported_catalog():
    models = model_router.get_supported_models()
    assert len(models) >= 6

    model_names = [m["model"] for m in models]
    assert "gemini-2.5-pro" in model_names
    assert "gemini-2.5-flash" in model_names
    assert "gpt-4o" in model_names
    assert "claude-3-5-sonnet" in model_names
    assert "nvidia/nemotron-4-340b-instruct" in model_names
    assert "llama3.1:8b" in model_names
