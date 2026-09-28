"""
AI Recommendation Engine Module for Phase 5.
Leverages Gemini Flash to produce structured job fit strengths, missing skills, and actionable recommendations.
Includes deterministic heuristic fallback for offline or zero-key environments.
"""
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from core.ai.gemini import GeminiFlashProvider
from core.config import settings
from core.logging import get_logger
from core.matching.base import CandidateProfileDTO, JobProfileDTO
from core.matching.experience_matcher import ExperienceMatchResult
from core.matching.role_matcher import RoleMatchResult
from core.matching.skill_matcher import SkillMatchResult

logger = get_logger("matching.recommendation")


@dataclass
class RecommendationResult:
    strengths: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# Curated learning roadmap recommendations for common technical competencies
TECH_RECOMMENDATIONS_MAP: Dict[str, str] = {
    "docker": "Learn Docker containerization fundamentals, container registries, and multi-stage builds.",
    "kubernetes": "Practice Kubernetes orchestration, Pod lifecycle management, and Helm deployment charts.",
    "k8s": "Practice Kubernetes orchestration, Pod lifecycle management, and Helm deployment charts.",
    "aws": "Complete AWS Cloud Practitioner or Solutions Architect Associate foundational labs.",
    "gcp": "Familiarize with Google Cloud Run, BigQuery, and IAM role architectures.",
    "azure": "Explore Azure App Services, Azure Blob Storage, and Entra ID authentication.",
    "ci/cd": "Set up automated GitHub Actions testing and deployment pipelines for your projects.",
    "graphql": "Build a GraphQL schema using Strawberry/Apollo with query and mutation resolvers.",
    "redis": "Implement Redis caching patterns, pub/sub messaging, and session persistence.",
    "kafka": "Study distributed event streaming, Kafka producer/consumer groups, and partitions.",
    "postgresql": "Deepen knowledge of PostgreSQL indexing strategies, transactions, and connection pooling.",
    "terraform": "Learn Infrastructure as Code (IaC) principles with Terraform and cloud providers.",
    "fastapi": "Construct asynchronous REST APIs in FastAPI with Pydantic validation and JWT auth.",
    "next.js": "Build fullstack React applications using Next.js App Router, SSR, and server actions.",
    "typescript": "Adopt strict TypeScript typing across frontend state management and API contracts.",
    "python": "Master advanced Python idioms, asyncio coroutines, and type annotations.",
    "pytorch": "Practice model fine-tuning and inference pipelines with PyTorch and Hugging Face.",
    "tensorflow": "Explore deep learning architecture prototyping with TensorFlow and Keras.",
}


class RecommendationGenerator:
    """
    Generates intelligent strengths, missing skills gap analysis, and tailored recommendations.
    Uses Gemini Flash with automatic deterministic fallback.
    """

    def __init__(self, ai_provider: Optional[GeminiFlashProvider] = None):
        self.ai_provider = ai_provider

    def _get_provider(self) -> Optional[GeminiFlashProvider]:
        if self.ai_provider:
            return self.ai_provider
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            try:
                self.ai_provider = GeminiFlashProvider()
                return self.ai_provider
            except Exception as exc:
                logger.warning(f"Could not initialize GeminiFlashProvider: {exc}")
        return None

    def generate_fallback(
        self,
        candidate: CandidateProfileDTO,
        job: JobProfileDTO,
        skill_result: SkillMatchResult,
        experience_result: ExperienceMatchResult,
        role_result: RoleMatchResult,
        overall_score: float,
    ) -> RecommendationResult:
        """Deterministic, high-quality fallback analysis."""
        strengths: List[str] = []
        recommendations: List[str] = []

        # 1. Strengths from matched skills
        if skill_result.matched_skills:
            top_skills = ", ".join(skill_result.matched_skills[:4])
            strengths.append(f"Demonstrated competence in core required technologies: {top_skills}.")

        # Strengths from experience
        if experience_result.candidate_years >= experience_result.required_years and experience_result.required_years > 0:
            strengths.append(
                f"Meets or exceeds the {experience_result.required_years}+ years experience requirement with {experience_result.candidate_years} years."
            )
        elif experience_result.candidate_years > 0:
            strengths.append(f"Possesses {experience_result.candidate_years} years of relevant industry experience.")

        # Strengths from role alignment
        if role_result.matched_role:
            strengths.append(f"Strong role alignment with target title '{job.title}'.")

        # Strengths from projects/portfolio
        if candidate.projects:
            strengths.append(f"Practical portfolio containing {len(candidate.projects)} demonstrated engineering projects.")

        if not strengths:
            strengths.append("Foundational technical background aligned with role domain.")

        # 2. Missing Skills
        missing = skill_result.missing_skills

        # 3. Actionable Recommendations
        for skill in missing[:4]:
            skill_lower = skill.lower().strip()
            rec = TECH_RECOMMENDATIONS_MAP.get(
                skill_lower,
                f"Develop practical project experience and build a GitHub demo utilizing {skill}.",
            )
            recommendations.append(rec)

        if not missing:
            recommendations.append(
                "Your technical skill set strongly aligns with this job. Tailor your resume summary and highlight relevant project achievements for this role."
            )
        elif len(recommendations) < 3:
            recommendations.append(
                f"Review {job.company}'s engineering tech stack and prepare targeted system architecture talking points."
            )

        return RecommendationResult(
            strengths=strengths,
            missing_skills=missing,
            recommendations=recommendations,
        )

    async def generate(
        self,
        candidate: CandidateProfileDTO,
        job: JobProfileDTO,
        skill_result: SkillMatchResult,
        experience_result: ExperienceMatchResult,
        role_result: RoleMatchResult,
        overall_score: float,
    ) -> RecommendationResult:
        """
        Generate gap analysis via Gemini Flash, falling back to deterministic generation.
        """
        provider = self._get_provider()
        if not provider:
            return self.generate_fallback(
                candidate, job, skill_result, experience_result, role_result, overall_score
            )

        prompt = f"""
Analyze the candidate's fit for this job posting and produce structured gap analysis.

Candidate Profile:
- Skills: {", ".join(candidate.skills)}
- Years of Experience: {candidate.years_of_experience}
- Preferred Roles: {", ".join(candidate.preferred_roles)}
- Education: {[e.get('degree', '') + ' in ' + str(e.get('field_of_study', '')) for e in candidate.educations]}

Job Listing:
- Title: {job.title}
- Company: {job.company}
- Location: {job.location}
- Requirements/Skills: {", ".join(job.skills)}
- Description Excerpt: {job.description[:400]}

Evaluation Signals:
- Overall Fit Score: {overall_score:.1f}%
- Matched Skills: {", ".join(skill_result.matched_skills)}
- Missing Skills: {", ".join(skill_result.missing_skills)}

Return strict JSON with this exact structure:
{{
  "strengths": [
    "Specific candidate strength 1",
    "Specific candidate strength 2"
  ],
  "missing_skills": [
    "Skill 1",
    "Skill 2"
  ],
  "recommendations": [
    "Concrete learning action or certification 1",
    "Concrete learning action or certification 2"
  ]
}}
"""
        system_instruction = (
            "You are an expert technical recruiter and AI career copilot. "
            "Produce crisp, actionable, high-quality candidate analysis in valid JSON."
        )

        try:
            raw_json = await provider.generate_json(prompt=prompt, system_instruction=system_instruction)
            parsed = json.loads(raw_json)
            strengths = parsed.get("strengths", [])
            missing_skills = parsed.get("missing_skills", skill_result.missing_skills)
            recommendations = parsed.get("recommendations", [])

            if isinstance(strengths, list) and isinstance(recommendations, list) and strengths and recommendations:
                return RecommendationResult(
                    strengths=[str(s) for s in strengths if s],
                    missing_skills=[str(m) for m in missing_skills if m],
                    recommendations=[str(r) for r in recommendations if r],
                )
        except Exception as exc:
            logger.warning(
                f"Gemini recommendation generation encountered an error; using fallback: {exc}"
            )

        return self.generate_fallback(
            candidate, job, skill_result, experience_result, role_result, overall_score
        )
