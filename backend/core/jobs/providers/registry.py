from typing import Dict, List, Optional
from core.jobs.providers.base import JobProvider
from core.jobs.providers.remoteok import RemoteOKProvider
from core.jobs.providers.greenhouse import GreenhouseProvider
from core.jobs.providers.lever import LeverProvider
from core.jobs.providers.wellfound import WellfoundProvider


class JobProviderRegistry:
    """
    Central registry for all active and extensible Job Providers.
    Initial: RemoteOK, Greenhouse, Lever, Wellfound.
    Future-ready: Naukri, Foundit, Indeed, Company Career Pages.
    """
    def __init__(self) -> None:
        self._providers: Dict[str, JobProvider] = {}
        self.register(RemoteOKProvider())
        self.register(GreenhouseProvider())
        self.register(LeverProvider())
        self.register(WellfoundProvider())

    def register(self, provider: JobProvider) -> None:
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: str) -> Optional[JobProvider]:
        return self._providers.get(name.strip().lower())

    def list_providers(self) -> List[JobProvider]:
        return list(self._providers.values())

    def provider_names(self) -> List[str]:
        return [p.name for p in self._providers.values()]


# Global singleton registry
job_provider_registry = JobProviderRegistry()
