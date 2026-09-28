"""
MatchingEngine Orchestrator Module for Phase 5.
Combines SkillMatcher, ExperienceMatcher, EducationMatcher, LocationMatcher,
RoleMatcher, and RecommendationGenerator with configurable weights.
"""
import time
from typing import List, Optional
from core.config import settings
from core.logging import get_logger
from core.matching.base import (
    CandidateProfileDTO,
    JobProfileDTO,
    MatchBreakdownDTO,
    ScoringWeights,
)
from core.matching.education_matcher import EducationMatcher
from core.matching.experience_matcher import ExperienceMatcher
from core.matching.location_matcher import LocationMatcher
from core.matching.recommendation_generator import RecommendationGenerator
from core.matching.role_matcher import RoleMatcher
from core.matching.skill_matcher import SkillMatcher

logger = get_logger("matching.engine")


class MatchingEngine:
    """
    Production-grade AI Job Matching Engine.
    Executes composite evaluation across skills, experience, roles, location, and education.
    """

    def __init__(
        self,
        skill_matcher: Optional[SkillMatcher] = None,
        experience_matcher: Optional[ExperienceMatcher] = None,
        education_matcher: Optional[EducationMatcher] = None,
        location_matcher: Optional[LocationMatcher] = None,
        role_matcher: Optional[RoleMatcher] = None,
        recommendation_generator: Optional[RecommendationGenerator] = None,
        weights: Optional[ScoringWeights] = None,
    ):
        self.skill_matcher = skill_matcher or SkillMatcher()
        self.experience_matcher = experience_matcher or ExperienceMatcher()
        self.education_matcher = education_matcher or EducationMatcher()
        self.location_matcher = location_matcher or LocationMatcher()
        self.role_matcher = role_matcher or RoleMatcher()
        self.recommendation_generator = recommendation_generator or RecommendationGenerator()
        self.weights = (weights or ScoringWeights()).normalize()

    async def score_job(
        self,
        candidate: CandidateProfileDTO,
        job: JobProfileDTO,
        generate_ai: bool = False,
    ) -> MatchBreakdownDTO:
        """
        Evaluate and score a single job against candidate profile.
        """
        skill_res = self.skill_matcher.match(candidate, job)
        exp_res = self.experience_matcher.match(candidate, job)
        role_res = self.role_matcher.match(candidate, job)
        loc_res = self.location_matcher.match(candidate, job)
        edu_res = self.education_matcher.match(candidate, job)

        overall = (
            self.weights.skill_weight * skill_res.score +
            self.weights.experience_weight * exp_res.score +
            self.weights.role_weight * role_res.score +
            self.weights.location_weight * loc_res.score +
            self.weights.education_weight * edu_res.score
        )
        overall_score = round(max(0.0, min(100.0, overall)), 1)

        if generate_ai:
            recs = await self.recommendation_generator.generate(
                candidate=candidate,
                job=job,
                skill_result=skill_res,
                experience_result=exp_res,
                role_result=role_res,
                overall_score=overall_score,
            )
        else:
            recs = self.recommendation_generator.generate_fallback(
                candidate=candidate,
                job=job,
                skill_result=skill_res,
                experience_result=exp_res,
                role_result=role_res,
                overall_score=overall_score,
            )

        return MatchBreakdownDTO(
            job_id=job.id,
            overall_score=overall_score,
            skill_score=skill_res.score,
            experience_score=exp_res.score,
            education_score=edu_res.score,
            location_score=loc_res.score,
            role_score=role_res.score,
            matched_skills=skill_res.matched_skills,
            missing_skills=skill_res.missing_skills,
            strengths=recs.strengths,
            recommendations=recs.recommendations,
        )

    async def match_jobs_batch(
        self,
        candidate: CandidateProfileDTO,
        jobs: List[JobProfileDTO],
        top_n_ai: int = 5,
    ) -> List[MatchBreakdownDTO]:
        """
        High-throughput batch evaluation.
        Evaluates 1000+ jobs in sub-second time.
        Enriches top N matches with AI recommendations if configured.
        """
        start_time = time.perf_counter()
        results: List[MatchBreakdownDTO] = []

        # Step 1: Fast in-memory scoring for all jobs
        for job in jobs:
            res = await self.score_job(candidate, job, generate_ai=False)
            results.append(res)

        # Step 2: Sort descending by overall match fit
        results.sort(key=lambda r: r.overall_score, reverse=True)

        # Step 3: Enrich top N matches with Gemini Flash if API key is present
        if top_n_ai > 0 and settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
            job_map = {j.id: j for j in jobs}
            for i in range(min(top_n_ai, len(results))):
                item = results[i]
                target_job = job_map.get(item.job_id)
                if target_job:
                    # Enrich with live Gemini Flash analysis
                    skill_res = self.skill_matcher.match(candidate, target_job)
                    exp_res = self.experience_matcher.match(candidate, target_job)
                    role_res = self.role_matcher.match(candidate, target_job)

                    ai_recs = await self.recommendation_generator.generate(
                        candidate=candidate,
                        job=target_job,
                        skill_result=skill_res,
                        experience_result=exp_res,
                        role_result=role_res,
                        overall_score=item.overall_score,
                    )
                    item.strengths = ai_recs.strengths
                    item.missing_skills = ai_recs.missing_skills
                    item.recommendations = ai_recs.recommendations

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Evaluated {len(jobs)} jobs in {duration_ms:.2f}ms",
            extra={"job_count": len(jobs), "duration_ms": duration_ms},
        )
        return results
