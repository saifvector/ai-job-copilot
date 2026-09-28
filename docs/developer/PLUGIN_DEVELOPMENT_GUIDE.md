# AI Job Copilot - Plugin SDK & Development Guide

The **Plugin SDK** enables developers to author modular, decoupled extensions for AI Job Copilot. Plugins can register custom job providers, enrich candidate analytics, and implement custom export targets.

---

## 1. Plugin Architecture

Plugins inherit from `BasePlugin` and are registered with the central `PluginRegistry` singleton.

```
                  ┌──────────────────────┐
                  │    PluginRegistry    │
                  └──────────┬───────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     │                       │                       │
┌────▼─────────────┐   ┌─────▼────────────┐   ┌──────▼────────────┐
│   NotionExport   │   │    GitHubJobs    │   │ CandidateDiversity│
│      Plugin      │   │      Plugin      │   │      Plugin       │
└──────────────────┘   └──────────────────┘   └───────────────────┘
  [on_custom_export]    [on_custom_job_prov]   [on_custom_analytics]
```

### Core Classes (`backend/plugins/sdk.py`)

1. **`PluginManifest`**: Metadata describing the plugin:
   - `id`: Unique slug (e.g. `notion_export`).
   - `name`: Human-readable name.
   - `version`: SemVer string (e.g. `1.0.0`).
   - `description`: Capabilities summary.
   - `author`: Developer or organization name.
   - `hooks`: List of lifecycle hooks supported.
   - `settings_schema`: Optional JSON Schema for configuration.
2. **`BasePlugin`**: Abstract base class.
   - `manifest`: Returns the `PluginManifest`.
   - `initialize(settings)`: Lifecycle hook invoked on startup.
   - `execute_hook(hook_name, **kwargs)`: Dispatches the execution request.
   - `teardown()`: Cleanup hook on shutdown.
3. **`PluginRegistry`**: Singleton manager:
   - `register(plugin)`: Registers and initializes a plugin instance.
   - `get_plugin(plugin_id)`: Retrieves a registered plugin by ID.
   - `list_plugins()`: Returns all active plugin manifests.
   - `execute_hook(hook_name, **kwargs)`: Executes all registered plugins declaring that hook.

---

## 2. Supported Lifecycle Hooks

| Hook Identifier | Signature | Purpose |
|---|---|---|
| `on_custom_job_provider` | `query: str, location: Optional[str] -> List[Dict]` | Fetch job opportunities from custom APIs, scrapers, or partner boards |
| `on_custom_analytics` | `candidate_data: Dict -> Dict` | Calculate proprietary suitability, readiness, or diversity scores |
| `on_custom_export` | `export_payload: Dict, format: str -> Dict` | Export tailored resumes, applications, or reports to external tools |

---

## 3. Creating a Custom Plugin

Here is a complete walkthrough for creating an **Airtable Application Tracker Plugin**:

```python
# backend/plugins/airtable_tracker_plugin.py
from typing import Any, Dict
from plugins.sdk import BasePlugin, PluginManifest

class AirtableTrackerPlugin(BasePlugin):
    """
    Syncs applications directly to an Airtable Base.
    """
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            id="airtable_tracker",
            name="Airtable Application Sync",
            version="1.0.0",
            description="Exports job application events directly into candidate Airtable bases",
            author="Ecosystem Partner",
            hooks=["on_custom_export"],
            settings_schema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string"},
                    "base_id": {"type": "string"},
                    "table_name": {"type": "string", "default": "Job Applications"},
                },
                "required": ["api_key", "base_id"],
            },
        )

    async def initialize(self, settings: Dict[str, Any]) -> None:
        self.api_key = settings.get("api_key")
        self.base_id = settings.get("base_id")
        self.table_name = settings.get("table_name", "Job Applications")

    async def execute_hook(self, hook_name: str, **kwargs) -> Any:
        if hook_name == "on_custom_export":
            payload = kwargs.get("export_payload", {})
            # Insert record into Airtable
            return {
                "success": True,
                "airtable_record_id": "rec987654321",
                "synced_job": payload.get("job_title", "Unknown"),
            }
        raise NotImplementedError(f"Hook {hook_name} not supported")
```

### Registering the Plugin

Register the plugin during startup in `backend/plugins/__init__.py`:

```python
from plugins.sdk import plugin_registry
from plugins.airtable_tracker_plugin import AirtableTrackerPlugin

airtable_plugin = AirtableTrackerPlugin()
plugin_registry.register(airtable_plugin)
```

Or dynamically via the Developer API:
```bash
curl -X POST "http://localhost:8000/api/v1/developer/plugins" \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "airtable_tracker",
    "name": "Airtable Application Sync",
    "version": "1.0.0",
    "hooks": ["on_custom_export"]
  }'
```

---

## 4. Built-in Reference Plugins

Phase 14 includes 3 production reference plugins:
1. `NotionExportPlugin` (`notion_export`): Exports resumes, applications, and reports into Notion databases. Declares `on_custom_export`.
2. `GitHubJobsPlugin` (`github_jobs`): Queries open technical roles from public GitHub/GitLab repositories. Declares `on_custom_job_provider`.
3. `CandidateDiversityAnalyticsPlugin` (`candidate_diversity_analytics`): Computes talent market representation and demographic inclusion benchmarking. Declares `on_custom_analytics`.
