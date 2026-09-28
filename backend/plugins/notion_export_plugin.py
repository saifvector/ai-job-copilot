from typing import Any, Dict, Optional
from plugins.sdk import BasePlugin, PluginManifest


class NotionExportPlugin(BasePlugin):
    """
    Plugin that formats reports and resume summaries into Notion-compatible Markdown blocks.
    """

    def __init__(self):
        manifest = PluginManifest(
            id="notion_exporter",
            name="Notion Markdown Exporter",
            version="1.1.0",
            author="Copilot Community Labs",
            description="Transforms career reports and application tracking summaries into structured Notion database markdown blocks.",
            capabilities=["custom_exporter"],
            is_active=True,
        )
        super().__init__(manifest)

    async def on_custom_export(self, export_format: str, report_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if export_format.lower() not in ["notion", "notion_md"]:
            return None

        title = report_data.get("title", "Career Intelligence Report")
        metrics = report_data.get("metrics", {})

        notion_blocks = [
            f"# 📌 {title}",
            "> Exported via AI Job Copilot Notion Integration Plugin",
            "",
            "## 📊 Key Highlights",
            f"- **Readiness Score**: {metrics.get('readiness_score', 85)}%",
            f"- **Active Applications**: {metrics.get('active_applications', 12)}",
            f"- **Interviews Scheduled**: {metrics.get('interviews_count', 3)}",
            "",
            "## 📝 Next Actions",
            "- [ ] Review pending recruiter responses",
            "- [ ] Prepare for upcoming technical interview",
        ]

        markdown_content = "\n".join(notion_blocks)
        return {
            "format": "notion_md",
            "filename": f"{title.lower().replace(' ', '_')}_notion.md",
            "content": markdown_content,
            "byte_size": len(markdown_content.encode("utf-8")),
        }
