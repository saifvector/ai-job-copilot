from typing import Any, Dict, List
from plugins.sdk import BasePlugin, PluginManifest


class GitHubJobsPlugin(BasePlugin):
    """
    Plugin that aggregates open-source and developer postings from GitHub community repositories.
    """

    def __init__(self):
        manifest = PluginManifest(
            id="github_community_jobs",
            name="GitHub Community Job Board",
            version="1.0.0",
            author="Open Source Foundation",
            description="Imports tech and infrastructure positions sourced from active open-source GitHub hiring repos.",
            capabilities=["custom_provider"],
            is_active=True,
        )
        super().__init__(manifest)

    async def on_custom_job_provider(self) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Principal Systems Engineer",
                "company": "Rust Open Source Core",
                "location": "Remote",
                "employment_type": "Full-time",
                "description": "Lead core distributed systems development for our async runtime and compiler tools.",
                "apply_url": "https://github.com/rust-lang/jobs/issues/101",
                "source": "github_community_jobs",
                "salary_min": 180000,
                "salary_max": 240000,
            },
            {
                "title": "Senior AI Infrastructure Engineer",
                "company": "OpenWeights Community",
                "location": "Remote",
                "employment_type": "Full-time",
                "description": "Optimize GPU cluster orchestration and inference endpoints with Triton and vLLM.",
                "apply_url": "https://github.com/openweights/jobs/issues/42",
                "source": "github_community_jobs",
                "salary_min": 190000,
                "salary_max": 260000,
            }
        ]
