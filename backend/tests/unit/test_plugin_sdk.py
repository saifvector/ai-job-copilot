import pytest
from plugins.sdk import BasePlugin, PluginManifest, PluginRegistry
from plugins.notion_export_plugin import NotionExportPlugin
from plugins.github_jobs_plugin import GitHubJobsPlugin
from plugins.candidate_diversity_plugin import CandidateDiversityAnalyticsPlugin


@pytest.mark.asyncio
async def test_plugin_registry_and_manifest():
    registry = PluginRegistry()
    plugins = registry.list_plugins()

    assert len(plugins) >= 3
    plugin_ids = [p.id for p in plugins]
    assert "notion_exporter" in plugin_ids
    assert "github_community_jobs" in plugin_ids
    assert "career_breadth_analytics" in plugin_ids


@pytest.mark.asyncio
async def test_notion_export_plugin():
    plugin = NotionExportPlugin()
    report_data = {
        "title": "Quarterly Career Velocity",
        "metrics": {"readiness_score": 92, "active_applications": 8},
    }

    res = await plugin.on_custom_export("notion", report_data)
    assert res is not None
    assert res["format"] == "notion_md"
    assert "📌 Quarterly Career Velocity" in res["content"]
    assert "92%" in res["content"]

    # Unsupported format returns None
    assert await plugin.on_custom_export("pdf", report_data) is None


@pytest.mark.asyncio
async def test_github_jobs_plugin():
    plugin = GitHubJobsPlugin()
    jobs = await plugin.on_custom_job_provider()

    assert len(jobs) >= 2
    assert jobs[0]["source"] == "github_community_jobs"
    assert "github.com" in jobs[0]["apply_url"]


@pytest.mark.asyncio
async def test_candidate_diversity_analytics_plugin():
    plugin = CandidateDiversityAnalyticsPlugin()
    context_data = {
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "AWS", "Terraform", "Redis"],
        "years_of_experience": 8,
    }

    res = await plugin.on_custom_analytics(context_data)
    metrics = res.get("career_breadth_metrics")

    assert metrics is not None
    assert metrics["versatility_score"] > 50.0
    assert metrics["skill_diversity_index"] == "High"
    assert metrics["leadership_readiness"] == "Senior/Principal"


@pytest.mark.asyncio
async def test_custom_dynamic_plugin_registration():
    registry = PluginRegistry()
    manifest = PluginManifest(
        id="custom_test_plugin",
        name="Dynamic Test Extension",
        version="0.1.0",
        description="Dynamic test extension plugin",
        capabilities=["custom_analytics"],
    )

    class CustomTestPlugin(BasePlugin):
        async def on_custom_analytics(self, context_data):
            c = dict(context_data)
            c["custom_flag"] = True
            return c

    plugin = CustomTestPlugin(manifest)
    registry.register(plugin)

    assert registry.get("custom_test_plugin") is not None

    dispatched = await registry.dispatch_analytics_hooks({"input": 1})
    assert dispatched.get("custom_flag") is True

    # Teardown / unregister
    registry.unregister("custom_test_plugin")
    assert registry.get("custom_test_plugin") is None
