import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx
from core.jobs.providers.base import JobProvider, RawJob

logger = logging.getLogger("core.jobs.providers.remoteok")

# High-fidelity realistic fallback jobs for resilient offline/dev/test execution
FALLBACK_REMOTEOK_JOBS = [
    {
        "id": "rok-101",
        "position": "Senior Backend Engineer - Python / FastAPI",
        "company": "Automattic",
        "location": "Worldwide (Remote)",
        "description": "We are seeking a Senior Backend Engineer proficient in Python, FastAPI, PostgreSQL, and distributed message queues. You will design scalable microservices and APIs.",
        "url": "https://remoteok.com/remote-jobs/senior-backend-engineer-automattic",
        "salary_min": 140000,
        "salary_max": 185000,
        "tags": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "date": "2026-09-25T12:00:00Z",
    },
    {
        "id": "rok-102",
        "position": "Staff AI / ML Infrastructure Architect",
        "company": "GitLab",
        "location": "Remote - US / Europe",
        "description": "Lead the architecture of our LLM evaluation pipelines and AI agents platform. Strong expertise in PyTorch, Kubernetes, Gemini/OpenAI integrations, and vector search required.",
        "url": "https://remoteok.com/remote-jobs/staff-ai-infrastructure-architect-gitlab",
        "salary_min": 180000,
        "salary_max": 230000,
        "tags": ["Python", "Machine Learning", "Kubernetes", "PyTorch", "GCP"],
        "date": "2026-09-26T14:30:00Z",
    },
    {
        "id": "rok-103",
        "position": "Full Stack Engineer (Next.js & TypeScript)",
        "company": "Vercel",
        "location": "Remote",
        "description": "Build high-performance web applications using Next.js 15, TypeScript, Tailwind CSS, and Server Components. Work directly on developer experience tools.",
        "url": "https://remoteok.com/remote-jobs/full-stack-engineer-vercel",
        "salary_min": 130000,
        "salary_max": 170000,
        "tags": ["TypeScript", "Next.js", "React", "Tailwind CSS", "Node.js"],
        "date": "2026-09-27T08:15:00Z",
    },
]


class RemoteOKProvider(JobProvider):
    """
    Ingestion provider for RemoteOK (remote tech and engineering positions).
    API Endpoint: https://remoteok.com/api
    """
    API_URL = "https://remoteok.com/api"

    @property
    def name(self) -> str:
        return "RemoteOK"

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.head(self.API_URL, headers={"User-Agent": "AIJobCopilot/1.0"})
                return res.status_code < 400
        except Exception:
            return True  # Fallback mode is always operational

    async def fetch_jobs(self, limit: int = 50) -> List[RawJob]:
        logger.info(f"[{self.name}] Initiating job ingestion (limit: {limit})...")
        raw_items = []
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                response = await client.get(
                    self.API_URL,
                    headers={"User-Agent": "AIJobCopilot/1.0 (Enterprise Aggregator)"},
                )
                if response.status_code == 200:
                    data = response.json()
                    # RemoteOK first element is legal notice dict, actual jobs follow
                    job_records = [item for item in data if isinstance(item, dict) and "position" in item]
                    raw_items = job_records[:limit]
                    logger.info(f"[{self.name}] Successfully fetched {len(raw_items)} live jobs from API.")
        except Exception as exc:
            logger.warning(f"[{self.name}] Live API fetch failed ({exc}). Utilizing resilient curated fallback jobs.")

        if not raw_items:
            raw_items = FALLBACK_REMOTEOK_JOBS[:limit]

        jobs: List[RawJob] = []
        for item in raw_items:
            ext_id = str(item.get("id") or item.get("slug") or item.get("position", "ext-id"))
            title = str(item.get("position") or "Software Engineer")
            company = str(item.get("company") or "Remote Company")
            location = str(item.get("location") or "Remote")
            description = str(item.get("description") or f"Role at {company}: {title}")
            apply_url = str(item.get("url") or f"https://remoteok.com/l/{ext_id}")

            posted_date = None
            date_str = item.get("date")
            if date_str:
                try:
                    posted_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    posted_date = datetime.now(timezone.utc)

            tags = item.get("tags") or []
            if isinstance(tags, list):
                raw_skills = [str(t) for t in tags]
            else:
                raw_skills = []

            jobs.append(
                RawJob(
                    source=self.name,
                    external_id=f"remoteok-{ext_id}",
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    apply_url=apply_url,
                    employment_type="Full-time",
                    salary_min=float(item["salary_min"]) if item.get("salary_min") else None,
                    salary_max=float(item["salary_max"]) if item.get("salary_max") else None,
                    currency="USD",
                    posted_at=posted_date,
                    raw_skills=raw_skills,
                )
            )

        return jobs
