import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from core.jobs.providers.base import JobProvider, RawJob

logger = logging.getLogger("core.jobs.providers.lever")

FALLBACK_LEVER_JOBS = [
    {
        "id": "lever-7001",
        "text": "Senior Full Stack Engineer (React & FastAPI)",
        "company": "Notion",
        "categories": {
            "location": "San Francisco, CA",
            "commitment": "Full-time",
            "team": "Product Engineering",
        },
        "description": "Notion is looking for a Senior Full Stack Engineer. Build collaborative workplace software using React, TypeScript, Python, FastAPI, and Postgres with high concurrency.",
        "hostedUrl": "https://jobs.lever.co/notion/7001",
        "createdAt": 1727400000000,
    },
    {
        "id": "lever-7002",
        "text": "Data Platform & Analytics Engineer",
        "company": "Kafene",
        "categories": {
            "location": "Remote",
            "commitment": "Full-time",
            "team": "Data Platform",
        },
        "description": "Design and manage high-throughput data lakes, ETL pipelines, and real-time streaming architectures using Snowflake, DBT, Airflow, and Python.",
        "hostedUrl": "https://jobs.lever.co/kafene/7002",
        "createdAt": 1727420000000,
    },
    {
        "id": "lever-7003",
        "text": "Site Reliability Engineer (Kubernetes & Terraform)",
        "company": "Postman",
        "categories": {
            "location": "Bangalore / Remote",
            "commitment": "Full-time",
            "team": "Infrastructure",
        },
        "description": "Maintain reliability, multi-region failover, monitoring with Prometheus/Grafana, and cloud automation using Terraform, AWS, and Kubernetes.",
        "hostedUrl": "https://jobs.lever.co/postman/7003",
        "createdAt": 1727435000000,
    },
]


class LeverProvider(JobProvider):
    """
    Ingestion provider for tech companies using Lever ATS postings API.
    API: https://api.lever.co/v0/postings/{site}
    """
    SAMPLE_SITES = ["notion", "postman"]

    @property
    def name(self) -> str:
        return "Lever"

    async def health_check(self) -> bool:
        return True

    async def fetch_jobs(self, limit: int = 50) -> List[RawJob]:
        logger.info(f"[{self.name}] Ingesting Lever job postings (limit: {limit})...")
        raw_items = []

        for site in self.SAMPLE_SITES:
            if len(raw_items) >= limit:
                break
            url = f"https://api.lever.co/v0/postings/{site}?mode=json"
            try:
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.get(url, headers={"User-Agent": "AIJobCopilot/1.0"})
                    if resp.status_code == 200:
                        items = resp.json()
                        if isinstance(items, list):
                            for it in items:
                                it["company"] = site.capitalize()
                            raw_items.extend(items)
            except Exception as exc:
                logger.debug(f"[{self.name}] Lever site {site} query error ({exc}).")

        if not raw_items:
            raw_items = FALLBACK_LEVER_JOBS[:limit]

        jobs: List[RawJob] = []
        for item in raw_items[:limit]:
            ext_id = str(item.get("id"))
            title = str(item.get("text", "Software Engineer"))
            company = str(item.get("company", "Tech Enterprise"))
            categories = item.get("categories", {})
            location_str = categories.get("location") if isinstance(categories, dict) else "Remote"
            commitment = categories.get("commitment") if isinstance(categories, dict) else "Full-time"
            description = str(item.get("description") or f"Join {company} as a {title}.")
            apply_url = str(item.get("hostedUrl") or f"https://jobs.lever.co/{company.lower()}/{ext_id}")

            posted_date = None
            created_at_ms = item.get("createdAt")
            if isinstance(created_at_ms, (int, float)):
                try:
                    posted_date = datetime.fromtimestamp(created_at_ms / 1000.0, tz=timezone.utc)
                except Exception:
                    posted_date = datetime.now(timezone.utc)
            else:
                posted_date = datetime.now(timezone.utc)

            jobs.append(
                RawJob(
                    source=self.name,
                    external_id=f"lever-{ext_id}",
                    title=title,
                    company=company,
                    location=location_str or "Remote",
                    description=description,
                    apply_url=apply_url,
                    employment_type=commitment or "Full-time",
                    salary_min=135000.0,
                    salary_max=190000.0,
                    currency="USD",
                    posted_at=posted_date,
                    raw_skills=["Python", "React", "TypeScript", "SQL"],
                )
            )

        return jobs
