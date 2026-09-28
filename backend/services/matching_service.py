"""
MatchingService for Phase 5 AI Job Matching Engine.
Coordinates candidate profile aggregation, batch job scoring, AI recommendation generation,
and database persistence.
Methods: runMatching, scoreJob, generateRecommendations, getTopMatches, getMatchResults.
"""
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from core.exceptions import NotFoundException
from core.logging import get_logger
from core.matching.base import CandidateProfileDTO, JobProfileDTO, MatchBreakdownDTO
from core.matching.engine import MatchingEngine
from models.job import JobModel
from models.match_result import MatchResultModel
from repositories.candidate_intelligence_repository import (
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.job_repository import JobRepository
from repositories.match_repository import MatchRepository
from repositories.profile_repository import ProfileRepository
from repositories.user_repository import UserRepository
from schemas.matching import MatchRunResponse

logger = get_logger("matching.service")


class MatchingService:
    """
    Primary intelligence service orchestrating candidate matching and AI gap recommendations.
    """

    def __init__(
        self,
        match_repo: MatchRepository,
        job_repo: JobRepository,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
        skill_repo: SkillRepository,
        experience_repo: ExperienceRepository,
        education_repo: EducationRepository,
        project_repo: ProjectRepository,
        matching_engine: Optional[MatchingEngine] = None,
    ):
        self.match_repo = match_repo
        self.job_repo = job_repo
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.skill_repo = skill_repo
        self.experience_repo = experience_repo
        self.education_repo = education_repo
        self.project_repo = project_repo
        self.matching_engine = matching_engine or MatchingEngine()

    async def build_candidate_profile(self, user_id: uuid.UUID) -> CandidateProfileDTO:
        """
        Aggregate all user profile and intelligence records into CandidateProfileDTO.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(resource="User", identifier=str(user_id))

        profile = await self.profile_repo.get_by_user_id(user_id)
        skills = await self.skill_repo.get_by_user_id(user_id)
        experiences = await self.experience_repo.get_by_user_id(user_id)
        educations = await self.education_repo.get_by_user_id(user_id)
        projects = await self.project_repo.get_by_user_id(user_id)

        skill_names = [s.name for s in skills]
        skill_confidences = {s.name: s.confidence_score for s in skills}

        exp_data = [
            {
                "role": e.role,
                "company": e.company,
                "description": e.description,
                "start_date": e.start_date,
                "end_date": e.end_date,
            }
            for e in experiences
        ]

        edu_data = [
            {
                "institution": ed.institution,
                "degree": ed.degree,
                "field_of_study": ed.field_of_study,
                "start_date": ed.start_date,
                "end_date": ed.end_date,
            }
            for ed in educations
        ]

        proj_data = [
            {
                "title": p.title,
                "description": p.description,
                "technologies": p.technologies or [],
            }
            for p in projects
        ]

        preferred_roles = profile.preferred_roles if (profile and profile.preferred_roles) else []
        preferred_locations = profile.preferred_locations if (profile and profile.preferred_locations) else []
        years_of_experience = profile.years_of_experience if profile else 0

        # If profile years is 0, estimate from experiences count
        if years_of_experience == 0 and experiences:
            years_of_experience = max(1, len(experiences))

        return CandidateProfileDTO(
            user_id=user_id,
            preferred_roles=preferred_roles,
            preferred_locations=preferred_locations,
            years_of_experience=years_of_experience,
            skills=skill_names,
            skill_confidences=skill_confidences,
            experiences=exp_data,
            educations=edu_data,
            projects=proj_data,
            summary=profile.summary if profile else None,
        )

    def _convert_job_to_dto(self, job: JobModel) -> JobProfileDTO:
        """Convert SQLAlchemy JobModel to JobProfileDTO."""
        skill_names = [s.skill_name for s in job.skills] if job.skills else []
        return JobProfileDTO(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            employment_type=job.employment_type,
            description=job.description,
            requirements=job.requirements,
            skills=skill_names,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            currency=job.currency or "USD",
            source=job.source,
            apply_url=job.apply_url,
        )

    async def runMatching(
        self,
        user_id: uuid.UUID,
        job_ids: Optional[List[uuid.UUID]] = None,
        limit: int = 500,
    ) -> MatchRunResponse:
        """
        Execute high-performance bulk matching for a candidate against available jobs.
        Target: < 2 seconds for 500 jobs.
        """
        start_time = time.perf_counter()

        candidate = await self.build_candidate_profile(user_id)

        # Retrieve jobs to evaluate
        if job_ids:
            jobs: List[JobModel] = []
            for jid in job_ids[:limit]:
                j = await self.job_repo.findById(jid)
                if j:
                    jobs.append(j)
        else:
            # Fetch up to limit active jobs
            jobs, _ = await self.job_repo.search(skip=0, limit=limit)

        if not jobs:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return MatchRunResponse(
                total_evaluated=0,
                matches_saved=0,
                top_score=0.0,
                duration_ms=round(duration_ms, 2),
            )

        job_dtos = [self._convert_job_to_dto(j) for j in jobs]

        # Execute high-throughput batch scoring
        scored_matches = await self.matching_engine.match_jobs_batch(
            candidate=candidate,
            jobs=job_dtos,
            top_n_ai=5,
        )

        # Bulk upsert into PostgreSQL
        saved_count = await self.match_repo.bulk_upsert_matches(user_id, scored_matches)

        top_score = scored_matches[0].overall_score if scored_matches else 0.0
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            f"Completed matching for user {user_id}: {saved_count} jobs scored in {duration_ms:.2f}ms",
            extra={"user_id": str(user_id), "evaluated": len(jobs), "duration_ms": duration_ms},
        )

        return MatchRunResponse(
            total_evaluated=len(jobs),
            matches_saved=saved_count,
            top_score=top_score,
            duration_ms=round(duration_ms, 2),
        )

    async def scoreJob(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        generate_ai: bool = False,
    ) -> MatchBreakdownDTO:
        """
        Score a single job against candidate profile and store result.
        """
        candidate = await self.build_candidate_profile(user_id)
        job = await self.job_repo.findById(job_id)
        if not job:
            raise NotFoundException(resource="Job", identifier=str(job_id))

        job_dto = self._convert_job_to_dto(job)
        breakdown = await self.matching_engine.score_job(
            candidate=candidate,
            job=job_dto,
            generate_ai=generate_ai,
        )

        # Upsert result
        await self.match_repo.bulk_upsert_matches(user_id, [breakdown])
        return breakdown

    async def generateRecommendations(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> MatchResultModel:
        """
        Generate on-demand Gemini Flash recommendations for a specific job match.
        """
        # Re-score with generate_ai=True
        await self.scoreJob(user_id=user_id, job_id=job_id, generate_ai=True)
        res = await self.match_repo.findByUserAndJob(user_id=user_id, job_id=job_id)
        if not res:
            raise NotFoundException(resource="MatchResult", identifier=f"{user_id}:{job_id}")
        return res

    async def getTopMatches(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
    ) -> List[MatchResultModel]:
        """
        Retrieve highest scoring matches for candidate, automatically running matching if empty.
        """
        results = await self.match_repo.findTopMatches(user_id=user_id, limit=limit)
        if not results:
            # Initial run if user has no match records yet
            await self.runMatching(user_id=user_id, limit=100)
            results = await self.match_repo.findTopMatches(user_id=user_id, limit=limit)
        return results

    async def getMatchResults(
        self,
        user_id: uuid.UUID,
        min_score: Optional[float] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[MatchResultModel], int]:
        """
        Faceted search and pagination across candidate's match results.
        """
        items, total = await self.match_repo.findByUser(
            user_id=user_id,
            min_score=min_score,
            location=location,
            company=company,
            role=role,
            skip=skip,
            limit=limit,
        )

        # If zero matches exist, trigger initial matching
        if total == 0 and min_score is None and not location and not company and not role:
            await self.runMatching(user_id=user_id, limit=100)
            items, total = await self.match_repo.findByUser(
                user_id=user_id,
                min_score=min_score,
                location=location,
                company=company,
                role=role,
                skip=skip,
                limit=limit,
            )

        return items, total
