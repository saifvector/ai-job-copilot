from typing import Any, Dict
from plugins.sdk import BasePlugin, PluginManifest


class CandidateDiversityAnalyticsPlugin(BasePlugin):
    """
    Plugin that augments match analytics with role diversity, seniority balance, and career breadth indicators.
    """

    def __init__(self):
        manifest = PluginManifest(
            id="career_breadth_analytics",
            name="Career Breadth & Seniority Analytics",
            version="1.2.0",
            author="Talent Analytics Initiative",
            description="Evaluates cross-functional skills adaptability and computes a career breadth score across candidate matches.",
            capabilities=["custom_analytics"],
            is_active=True,
        )
        super().__init__(manifest)

    async def on_custom_analytics(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        augmented = dict(context_data)
        skills = context_data.get("skills", [])
        experience_years = context_data.get("years_of_experience", 0)

        # Compute dynamic versatility multiplier
        versatility_score = min(100.0, round((len(skills) * 4.5) + (experience_years * 3.0), 1))
        augmented["career_breadth_metrics"] = {
            "versatility_score": versatility_score,
            "skill_diversity_index": "High" if len(skills) >= 8 else "Moderate",
            "leadership_readiness": "Senior/Principal" if experience_years >= 6 else "Mid-Level",
        }
        return augmented
