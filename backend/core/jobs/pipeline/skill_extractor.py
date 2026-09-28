import json
import logging
import os
import re
from typing import List, Set
from google import genai
from google.genai import types

logger = logging.getLogger("core.jobs.pipeline.skill_extractor")

# Deterministic tech dictionary for high-accuracy local & fallback extraction
COMMON_TECH_SKILLS = [
    "Python", "FastAPI", "PostgreSQL", "React", "TypeScript", "JavaScript", "Docker", "Kubernetes",
    "AWS", "GCP", "Azure", "Next.js", "Node.js", "GraphQL", "REST", "SQL", "Redis", "Kafka",
    "MongoDB", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Git", "CI/CD", "Linux", "Terraform",
    "Tailwind CSS", "Go", "Rust", "Java", "C++", "C#", ".NET", "Microservices", "Elasticsearch",
    "Snowflake", "dbt", "Airflow", "Celery", "RabbitMQ", "Supabase", "Prisma", "SQLAlchemy",
    "LLM", "Generative AI", "NLP", "Scikit-Learn", "Vue.js", "Angular", "WebSockets"
]


class JobSkillExtractor:
    """
    Extracts relevant technical and domain skills from job descriptions.
    Uses Gemini Flash (gemini-2.5-flash) with structured JSON extraction.
    Resilient fallback ensures 100% operation even offline or without API keys.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")
        self._client: genai.Client | None = None
        if self.api_key and not self.api_key.startswith("mock_"):
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                logger.warning(f"Failed to initialize Gemini Flash client: {exc}")

    async def extract_skills(self, description: str, seed_skills: List[str] | None = None) -> List[str]:
        """
        Extracts skills from description text using Gemini Flash or fallback pattern extraction.
        """
        extracted: Set[str] = set()

        # Include any seed skills from the provider (e.g. RemoteOK tags)
        if seed_skills:
            for s in seed_skills:
                cleaned = s.strip()
                if cleaned and len(cleaned) <= 50:
                    extracted.add(cleaned)

        # If Gemini client is configured, call Gemini Flash
        if self._client:
            try:
                prompt = (
                    "You are a technical recruiter and parsing assistant.\n"
                    "Extract the top technical skills, frameworks, languages, tools, and domain concepts mentioned in this job description.\n"
                    "Return ONLY valid JSON in the exact format:\n"
                    '{\n  "skills": ["Python", "FastAPI", "PostgreSQL"]\n}\n\n'
                    f"Job Description:\n{description[:4000]}"
                )
                response = await self._client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )
                if response and response.text:
                    parsed = json.loads(response.text.strip())
                    ai_skills = parsed.get("skills", [])
                    if isinstance(ai_skills, list):
                        for sk in ai_skills:
                            if isinstance(sk, str) and sk.strip():
                                extracted.add(sk.strip())
            except Exception as exc:
                logger.debug(f"Gemini Flash skill extraction error: {exc}. Using deterministic extractor.")

        # If few skills were found, run regex pattern scan against COMMON_TECH_SKILLS
        if len(extracted) < 3 and description:
            desc_lower = description.lower()
            for skill in COMMON_TECH_SKILLS:
                # Word boundary match
                pattern = r"\b" + re.escape(skill.lower()) + r"\b"
                if re.search(pattern, desc_lower):
                    extracted.add(skill)

        # Clean and sort skills
        clean_list = [s for s in extracted if len(s) >= 2 and len(s) <= 50]
        return sorted(clean_list)[:15]  # Cap at 15 key skills per job
