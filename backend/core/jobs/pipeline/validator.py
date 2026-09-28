from typing import Optional, Tuple
from core.jobs.providers.base import RawJob


class JobValidator:
    """
    Validates normalized job data before deduplication and database persistence.
    """

    @staticmethod
    def validate(job: RawJob) -> Tuple[bool, Optional[str]]:
        if not job.title or len(job.title.strip()) < 2:
            return False, "Job title is required (minimum 2 characters)"

        if not job.company or len(job.company.strip()) < 2:
            return False, "Company name is required (minimum 2 characters)"

        if not job.apply_url or not (job.apply_url.startswith("http://") or job.apply_url.startswith("https://")):
            return False, f"Invalid apply URL: {job.apply_url}"

        if not job.description or len(job.description.strip()) < 10:
            return False, "Job description is too short (minimum 10 characters)"

        if not job.source or not job.external_id:
            return False, "Source and external_id must not be empty"

        return True, None
