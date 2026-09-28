from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field


class PluginManifest(BaseModel):
    id: str = Field(..., description="Unique alphanumeric identifier (e.g. 'notion_exporter')")
    name: str = Field(..., description="Human-readable title")
    version: str = Field(default="1.0.0", description="SemVer string")
    author: str = Field(default="Third-Party Developer")
    description: str = Field(..., description="Plugin description")
    capabilities: List[str] = Field(
        default=[],
        description="Supported extension points: 'custom_provider', 'custom_analytics', 'custom_exporter'",
    )
    is_active: bool = True
    config_schema: Optional[Dict[str, Any]] = None


class BasePlugin(ABC):
    """
    Abstract base class for all third-party plugins in the AI Job Copilot ecosystem.
    Plugins can register hooks to extend job search providers, scoring analytics, or document exporters.
    """

    def __init__(self, manifest: PluginManifest, config: Optional[Dict[str, Any]] = None):
        self.manifest = manifest
        self.config = config or {}

    @property
    def plugin_id(self) -> str:
        return self.manifest.id

    def initialize(self) -> None:
        """Called upon plugin activation."""
        pass

    def teardown(self) -> None:
        """Called upon plugin deactivation or unload."""
        pass

    # --- Extension Hooks ---

    async def on_custom_job_provider(self) -> List[Dict[str, Any]]:
        """Hook to provide custom external job listings."""
        return []

    async def on_custom_analytics(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook to augment matching analytics or profile diagnostics."""
        return context_data

    async def on_custom_export(self, export_format: str, report_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hook to export application/resume/report data to a custom format."""
        return None


class PluginRegistry:
    """
    Singleton registry managing active plugins, hook dispatches, and runtime configurations.
    """
    _instance: Optional["PluginRegistry"] = None

    def __new__(cls) -> "PluginRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins = {}
        return cls._instance

    def register(self, plugin: BasePlugin) -> None:
        plugin.initialize()
        self._plugins[plugin.plugin_id] = plugin

    def unregister(self, plugin_id: str) -> bool:
        plugin = self._plugins.pop(plugin_id, None)
        if plugin:
            plugin.teardown()
            return True
        return False

    def get(self, plugin_id: str) -> Optional[BasePlugin]:
        return self._plugins.get(plugin_id)

    def list_plugins(self) -> List[PluginManifest]:
        return [p.manifest for p in self._plugins.values()]

    async def dispatch_job_providers(self) -> List[Dict[str, Any]]:
        results = []
        for p in self._plugins.values():
            if "custom_provider" in p.manifest.capabilities:
                jobs = await p.on_custom_job_provider()
                results.extend(jobs)
        return results

    async def dispatch_analytics_hooks(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(context_data)
        for p in self._plugins.values():
            if "custom_analytics" in p.manifest.capabilities:
                result = await p.on_custom_analytics(result)
        return result

    async def dispatch_custom_export(self, export_format: str, report_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for p in self._plugins.values():
            if "custom_exporter" in p.manifest.capabilities:
                exported = await p.on_custom_export(export_format, report_data)
                if exported is not None:
                    return exported
        return None
