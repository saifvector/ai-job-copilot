import hashlib
import re
from typing import Set
from core.jobs.providers.base import RawJob


class JobDeduplicator:
    """
    Prevents duplicate job postings across providers and repeated sync runs.
    Uses: Company + Job Title + Apply URL.
    """

    @staticmethod
    def _clean_str(text: str) -> str:
        # Lowercase and strip non-alphanumeric chars
        return re.sub(r"[^\w\s]", "", (text or "").lower()).strip()

    @classmethod
    def generate_dedup_key(cls, company: str, title: str, apply_url: str) -> str:
        clean_company = cls._clean_str(company)
        clean_title = cls._clean_str(title)
        # Normalize URL without protocol or tracking
        clean_url = re.sub(r"^https?://", "", (apply_url or "").lower().rstrip("/"))
        clean_url = clean_url.split("?")[0]

        raw_key = f"{clean_company}|{clean_title}|{clean_url}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @classmethod
    def get_job_key(cls, job: RawJob) -> str:
        return cls.generate_dedup_key(job.company, job.title, job.apply_url)

    @classmethod
    def filter_batch_duplicates(cls, jobs: list[RawJob], seen_keys: Set[str]) -> tuple[list[RawJob], int]:
        """
        Deduplicates an in-memory batch of raw jobs and updates the seen_keys set.
        Returns: (unique_jobs, skipped_count)
        """
        unique_jobs: list[RawJob] = []
        skipped = 0

        for job in jobs:
            key = cls.get_job_key(job)
            if key in seen_keys:
                skipped += 1
                continue
            seen_keys.add(key)
            unique_jobs.append(job)

        return unique_jobs, skipped
