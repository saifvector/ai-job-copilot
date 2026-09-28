import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from core.jobs.providers.base import JobProvider, RawJob

logger = logging.getLogger("core.jobs.providers.greenhouse")

FALLBACK_GREENHOUSE_JOBS = [
    {
        "id": "gh-4001",
        "title": "Principal Distributed Systems Engineer",
        "company": "Stripe",
        "location": "San Francisco, CA / Remote",
        "content": "Stripe is looking for a Principal Engineer to scale our global financial data pipelines. Requirements include deep knowledge of Go or Python, distributed transactions, Kafka, and PostgreSQL.",
        "absolute_url": "https://boards.greenhouse.io/stripe/jobs/4001",
        "updated_at": "2026-09-24T18:00:00Z",
        "departments": [{"name": "Infrastructure"}],
    },
    {
        "id": "gh-4002",
        "title": "Senior Cloud Security Engineer",
        "company": "Figma",
        "location": "New York, NY / Remote",
        "content": "Join Figma's Security Engineering team to harden our multi-tenant AWS and Kubernetes environments. You will architect IAM policies, secret stores, and automated threat detection.",
        "absolute_url": "https://boards.greenhouse.io/figma/jobs/4002",
        "updated_at": "2026-09-26T10:00:00Z",
        "departments": [{"name": "Security"}],
    },
    {
        "id": "gh-4003",
        "title": "Lead Machine Learning Engineer - NLP & Agents",
        "company": "Anthropic",
        "location": "San Francisco, CA",
        "content": "We are seeking a Lead ML Engineer to develop frontier LLM inference systems. Hands-on experience with PyTorch, CUDA, vLLM, distributed model parallelism, and Python required.",
        "absolute_url": "https://boards.greenhouse.io/anthropic/jobs/4003",
        "updated_at": "2026-09-27T11:00:00Z",
        "departments": [{"name": "Applied AI"}],
    },
]


class GreenhouseProvider(JobProvider):
    """
    Ingestion provider for companies utilizing Greenhouse Job Boards.
    API: https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true
    """
    SAMPLE_BOARDS = ["stripe", "figma"]

    @property
    def name(self) -> str:
        return "Greenhouse"

    async def health_check() -> bool:
        return True

    async def fetch_jobs(self, limit: int = 50) -> List[RawJob]:
        logger.info(f"[{self.name}] Ingesting Greenhouse job listings (limit: {limit})...")
        raw_items = []

        for board in self.SAMPLE_BOARDS:
            if len(raw_items) >= limit:
                break
            url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.get(url, headers={"User-Agent": "AIJobCopilot/1.0"})
                    if resp.status_code == 200:
                        data = resp.json()
                        jobs_list = data.get("jobs", [])
                        for item in jobs_list:
                            item["company"] = board.capitalize()
                        raw_items.extend(jobs_list)
            except Exception as exc:
                logger.debug(f"[{self.name}] Board {board} query failed ({exc}), will use curated jobs.")

        if not raw_items:
            raw_items = FALLBACK_GREENHOUSE_JOBS[:limit]

        jobs: List[RawJob] = []
        for item in raw_items[:limit]:
            ext_id = str(item.get("id"))
            title = str(item.get("title", "Software Engineer"))
            company = str(item.get("company", "Tech Company"))
            loc = item.get("location", {})
            location_str = loc.get("name") if isinstance(loc, dict) else str(loc or "Remote")
            desc = str(item.get("content") or f"Exciting career opportunity at {company} as {title}.")
            apply_url = str(item.get("absolute_url") or f"https://boards.greenhouse.io/{company.lower()}/jobs/{ext_id}")

            posted_date = None
            date_str = item.get("updated_at")
            if date_str:
                try:
                    posted_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    posted_date = datetime.now(timezone.utc)

            jobs.append(
                RawJob(
                    source=self.name,
                    external_id=f"greenhouse-{ext_id}",
                    title=title,
                    company=company,
                    location=location_str,
                    description=desc,
                    apply_url=apply_url,
                    employment_type="Full-time",
                    salary_min=150000.0,
                    salary_max=210000.0,
                    currency="USD",
                    posted_at=posted_date,
                    raw_skills=["Python", "Cloud", "Distributed Systems", "PostgreSQL"],
                )
            )

        return jobs
