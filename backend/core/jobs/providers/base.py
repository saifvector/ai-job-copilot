from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RawJob:
    """
    Normalized data carrier emitted by any JobProvider before pipeline ingestion.
    """
    source: str
    external_id: str
    title: str
    company: str
    location: str
    description: str
    apply_url: str
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "USD"
    requirements: Optional[str] = None
    company_website: Optional[str] = None
    posted_at: Optional[datetime] = None
    raw_skills: List[str] = field(default_factory=list)


class JobProvider(ABC):
    """
    Abstract base provider defining standard contract for all external job aggregators.
    Subclasses: RemoteOKProvider, GreenhouseProvider, LeverProvider, WellfoundProvider.
    Future Ready: NaukriProvider, FounditProvider, IndeedProvider, CareerPagesProvider.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical name of the job provider (e.g. 'RemoteOK', 'Greenhouse')."""
        pass

    @abstractmethod
    async def fetch_jobs(self, limit: int = 50) -> List[RawJob]:
        """
        Fetch and parse latest job postings from the external source.
        Returns a list of raw job instances ready for the ingestion pipeline.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify upstream API or service availability."""
        pass
