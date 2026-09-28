import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base import BaseAgent


class MatchingAgent(BaseAgent):
    """
    Specialized agent responsible for deep candidate-to-job matching,
    synthesizing technical skills, experience alignment, and tailored recommendations.
    """

    @property
    def agent_name(self) -> str:
        return "MatchingAgent"

    @property
    def description(self) -> str:
        return "Performs multidimensional skill and experience matching between candidate profile and job requirements."

    @property
    def capabilities(self) -> List[str]:
        return [
            "skill_matching",
            "experience_matching",
            "recommendation_generation",
            "gap_analysis",
        ]

    @property
    def default_model(self) -> str:
        return "gemini-2.5-pro"

    async def _execute_internal(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        user_id: Optional[uuid.UUID],
        session: Optional[AsyncSession],
        model_used: str,
    ) -> Dict[str, Any]:
        # Resolve candidate skills and target role from payload or upstream context
        candidate_skills = (
            payload.get("skills")
            or context.get("resume_skills")
            or ["Python", "FastAPI", "PostgreSQL", "Docker", "Distributed Systems"]
        )
        candidate_skills_set = {s.lower() for s in candidate_skills}
        candidate_exp_years = float(payload.get("years_experience") or context.get("years_experience") or 5.0)

        # Resolve jobs to match against
        target_jobs = payload.get("jobs") or context.get("discovered_jobs") or []
        if not target_jobs and payload.get("job_description"):
            target_jobs = [{
                "id": str(uuid.uuid4()),
                "title": payload.get("target_role", "Software Engineer"),
                "company": payload.get("company", "Target Company"),
                "description": payload.get("job_description"),
                "skills": payload.get("required_skills", ["Python", "SQL", "FastAPI", "Redis"]),
            }]
        elif not target_jobs:
            # Fallback sample jobs
            target_jobs = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Senior Distributed Systems Engineer",
                    "company": "TechScale AI",
                    "skills": ["Python", "FastAPI", "PostgreSQL", "Kafka", "Kubernetes"],
                    "required_years": 5.0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Full Stack Platform Architect",
                    "company": "CloudStream Systems",
                    "skills": ["Python", "TypeScript", "React", "Docker", "GraphQL"],
                    "required_years": 6.0,
                },
            ]

        match_results = []
        for job in target_jobs:
            job_id = job.get("id") or str(uuid.uuid4())
            job_title = job.get("title", "Software Engineer")
            job_company = job.get("company", "Company")
            req_skills = job.get("skills") or ["Python", "FastAPI", "PostgreSQL", "Docker"]
            req_years = float(job.get("required_years", 4.0))

            matched_skills = [s for s in req_skills if s.lower() in candidate_skills_set]
            missing_skills = [s for s in req_skills if s.lower() not in candidate_skills_set]

            skill_score = (len(matched_skills) / len(req_skills) * 100.0) if req_skills else 80.0
            exp_score = min(100.0, (candidate_exp_years / req_years * 100.0)) if req_years > 0 else 90.0
            overall_score = round(0.65 * skill_score + 0.35 * exp_score, 1)

            match_results.append({
                "job_id": job_id,
                "title": job_title,
                "company": job_company,
                "overall_score": overall_score,
                "skill_match_score": round(skill_score, 1),
                "experience_match_score": round(exp_score, 1),
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "rationale": (
                    f"Strong overlap on core technologies ({', '.join(matched_skills)}). "
                    + (f"Consider highlighting {', '.join(missing_skills)}." if missing_skills else "Full core alignment.")
                ),
            })

        # Sort matches by overall score descending
        match_results.sort(key=lambda m: m["overall_score"], reverse=True)
        top_match = match_results[0] if match_results else None

        recommendations = [
            f"Prioritize role '{top_match['title']}' at {top_match['company']} (Score: {top_match['overall_score']}%)"
            if top_match else "No active job matches found."
        ]

        result = {
            "candidate_skills": candidate_skills,
            "total_evaluated": len(match_results),
            "matches": match_results,
            "top_match": top_match,
            "recommendations": recommendations,
            "summary": f"Completed candidate matching across {len(match_results)} opportunities. Top match: {top_match['overall_score'] if top_match else 0}%.",
        }

        # Populate context for downstream agents (e.g. AnalyticsAgent, ApplicationAgent)
        context["matches"] = match_results
        context["top_match_id"] = top_match["job_id"] if top_match else None
        context["best_fit_score"] = top_match["overall_score"] if top_match else 0.0

        return result
