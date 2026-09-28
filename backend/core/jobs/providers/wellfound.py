import logging
from datetime import datetime, timezone
from typing import List, Optional
from core.jobs.providers.base import JobProvider, RawJob

logger = logging.getLogger("core.jobs.providers.wellfound")

CURATED_WELLFOUND_STARTUP_JOBS = [
    {
        "id": "wf-9001",
        "title": "Founding AI Engineer (Autonomous Agents)",
        "company": "Cognition",
        "location": "San Francisco, CA / Remote",
        "description": "We are looking for a Founding AI Engineer to build code generation models and agent reasoning loops. Strong background in Python, LLM evaluation, tree search, and distributed training required.",
        "apply_url": "https://wellfound.com/company/cognition/jobs/9001",
        "salary_min": 170000,
        "salary_max": 240000,
        "employment_type": "Full-time",
        "posted_at": "2026-09-25T16:00:00Z",
        "tags": ["Python", "FastAPI", "AI Agents", "PyTorch", "Docker"],
    },
    {
        "id": "wf-9002",
        "title": "Lead Product Engineer (Next.js & Supabase)",
        "company": "Linear",
        "location": "Remote (Worldwide)",
        "description": "Help design and build the fastest issue tracking and project management software in the world. Deep mastery of React, Next.js, WebSockets, Local-first sync, and TypeScript.",
        "apply_url": "https://wellfound.com/company/linear/jobs/9002",
        "salary_min": 160000,
        "salary_max": 210000,
        "employment_type": "Full-time",
        "posted_at": "2026-09-26T09:30:00Z",
        "tags": ["React", "TypeScript", "Next.js", "WebSockets", "PostgreSQL"],
    },
    {
        "id": "wf-9003",
        "title": "DevOps & Cloud Infrastructure Lead",
        "company": "Railway",
        "location": "Remote",
        "description": "Design and manage the developer platform engine powering thousands of containers worldwide. Kubernetes, Rust/Go, Linux kernels, and multi-cloud networking.",
        "apply_url": "https://wellfound.com/company/railway/jobs/9003",
        "salary_min": 155000,
        "salary_max": 205000,
        "employment_type": "Full-time",
        "posted_at": "2026-09-27T07:45:00Z",
        "tags": ["Kubernetes", "Docker", "Go", "Terraform", "AWS"],
    },
    {
        "id": "wf-9004",
        "title": "Senior Frontend Engineer (Design Systems)",
        "company": "Perplexity AI",
        "location": "San Francisco, CA",
        "description": "Craft exceptional conversational AI search experiences. Design systems with Tailwind CSS, React 19, framer-motion, and micro-interactions.",
        "apply_url": "https://wellfound.com/company/perplexity/jobs/9004",
        "salary_min": 150000,
        "salary_max": 195000,
        "employment_type": "Full-time",
        "posted_at": "2026-09-27T10:15:00Z",
        "tags": ["React", "TypeScript", "Tailwind CSS", "UI/UX", "Next.js"],
    },
]


class WellfoundProvider(JobProvider):
    """
    Ingestion provider for startup and venture-backed roles from Wellfound (AngelList).
    """
    @property
    def name(self) -> str:
        return "Wellfound"

    async def health_check(self) -> bool:
        return True

    async def fetch_jobs(self, limit: int = 50) -> List[RawJob]:
        logger.info(f"[{self.name}] Fetching curated startup jobs (limit: {limit})...")
        items = CURATED_WELLFOUND_STARTUP_JOBS[:limit]
        jobs: List[RawJob] = []

        for item in items:
            posted_date = None
            date_str = item.get("posted_at")
            if date_str:
                try:
                    posted_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    posted_date = datetime.now(timezone.utc)

            jobs.append(
                RawJob(
                    source=self.name,
                    external_id=f"wellfound-{item['id']}",
                    title=item["title"],
                    company=item["company"],
                    location=item["location"],
                    description=item["description"],
                    apply_url=item["apply_url"],
                    employment_type=item.get("employment_type", "Full-time"),
                    salary_min=float(item.get("salary_min", 0)),
                    salary_max=float(item.get("salary_max", 0)),
                    currency="USD",
                    posted_at=posted_date,
                    raw_skills=item.get("tags", []),
                )
            )

        return jobs
