from plugins.sdk import BasePlugin, PluginManifest, PluginRegistry
from plugins.notion_export_plugin import NotionExportPlugin
from plugins.github_jobs_plugin import GitHubJobsPlugin
from plugins.candidate_diversity_plugin import CandidateDiversityAnalyticsPlugin

# Auto-register reference plugins in singleton registry
_registry = PluginRegistry()
_registry.register(NotionExportPlugin())
_registry.register(GitHubJobsPlugin())
_registry.register(CandidateDiversityAnalyticsPlugin())

__all__ = [
    "BasePlugin",
    "PluginManifest",
    "PluginRegistry",
    "NotionExportPlugin",
    "GitHubJobsPlugin",
    "CandidateDiversityAnalyticsPlugin",
]
