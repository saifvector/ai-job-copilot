import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from core.jobs.pipeline.deduplicator import JobDeduplicator
from core.jobs.pipeline.normalizer import JobNormalizer
from core.jobs.pipeline.skill_extractor import JobSkillExtractor
from core.jobs.pipeline.validator import JobValidator
from core.jobs.providers.registry import job_provider_registry
from models.job import JobModel
from repositories.job_repository import JobRepository
from schemas.job import JobFilterParams, JobListResponse, JobResponse, JobSyncResponse

logger = logging.getLogger("services.job_service")


class JobService:
    """
    High-level orchestration service for Job Discovery, Ingestion, Deduplication, and Search.
    Methods per specification: syncJobs, searchJobs, getJob, extractSkills.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = JobRepository(session)
        self.normalizer = JobNormalizer()
        self.validator = JobValidator()
        self.deduplicator = JobDeduplicator()
        self.skill_extractor = JobSkillExtractor()

    async def sync_jobs(
        self,
        source: Optional[str] = None,
        limit_per_source: int = 50,
    ) -> JobSyncResponse:
        """
        Executes full ingestion pipeline across job providers:
        Provider -> Raw Job -> Normalizer -> Validator -> Deduplicator -> SkillExtractor -> Database.
        """
        start_time = time.perf_counter()
        logger.info(f"Starting job synchronization (source filter: {source or 'ALL'})...")

        if source and source.strip():
            provider = job_provider_registry.get_provider(source.strip())
            providers = [provider] if provider else []
        else:
            providers = job_provider_registry.list_providers()

        synced_count = 0
        duplicates_skipped = 0
        errors_count = 0
        source_counts: Dict[str, int] = {}
        seen_batch_keys: set = set()

        for prov in providers:
            source_name = prov.name
            source_counts[source_name] = 0
            try:
                raw_jobs = await prov.fetch_jobs(limit=limit_per_source)
                logger.info(f"[{source_name}] Retrieved {len(raw_jobs)} raw candidate jobs.")

                for raw_job in raw_jobs:
                    try:
                        # Step 1: Normalize
                        norm_job = self.normalizer.normalize(raw_job)

                        # Step 2: Validate
                        is_valid, error_msg = self.validator.validate(norm_job)
                        if not is_valid:
                            logger.warning(f"[{source_name}] Rejected invalid job ({error_msg}): {norm_job.title}")
                            errors_count += 1
                            continue

                        # Step 3: In-batch and Database Deduplication
                        batch_key = self.deduplicator.get_job_key(norm_job)
                        if batch_key in seen_batch_keys:
                            duplicates_skipped += 1
                            continue

                        # Check database for existing external_id or company+title+url duplicate
                        existing_job = await self.repository.find_by_external_id(norm_job.source, norm_job.external_id)
                        if not existing_job:
                            existing_job = await self.repository.find_by_deduplication_key(
                                norm_job.company, norm_job.title, norm_job.apply_url
                            )

                        if existing_job:
                            duplicates_skipped += 1
                            seen_batch_keys.add(batch_key)
                            continue

                        seen_batch_keys.add(batch_key)

                        # Step 4: Extract skills with Gemini Flash / fallback
                        skills = await self.skill_extractor.extract_skills(
                            norm_job.description, seed_skills=norm_job.raw_skills
                        )

                        # Step 5: Store in database
                        job_dict = {
                            "source": norm_job.source,
                            "external_id": norm_job.external_id,
                            "title": norm_job.title,
                            "company": norm_job.company,
                            "location": norm_job.location,
                            "employment_type": norm_job.employment_type,
                            "salary_min": norm_job.salary_min,
                            "salary_max": norm_job.salary_max,
                            "currency": norm_job.currency,
                            "description": norm_job.description,
                            "requirements": norm_job.requirements,
                            "apply_url": norm_job.apply_url,
                            "company_website": norm_job.company_website,
                            "posted_at": norm_job.posted_at,
                        }

                        await self.repository.create_job(job_dict, skills=skills)
                        synced_count += 1
                        source_counts[source_name] += 1

                    except Exception as item_err:
                        logger.error(f"[{source_name}] Failed to ingest job item: {item_err}")
                        errors_count += 1

            except Exception as prov_err:
                logger.error(f"[{source_name}] Provider synchronization failure: {prov_err}")
                errors_count += 1

        await self.session.commit()
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        message = f"Synchronized {synced_count} jobs from {len(providers)} sources. {duplicates_skipped} duplicates skipped ({duration_ms}ms)."
        logger.info(message)

        return JobSyncResponse(
            synced_count=synced_count,
            duplicates_skipped=duplicates_skipped,
            errors_count=errors_count,
            sources=source_counts,
            duration_ms=duration_ms,
            message=message,
        )

    # Alias per specification
    syncJobs = sync_jobs

    async def search_jobs(self, params: JobFilterParams) -> JobListResponse:
        """
        Executes faceted search with pagination and sorting.
        """
        skip = (params.page - 1) * params.page_size
        jobs, total = await self.repository.search(
            query=params.query,
            role=params.role,
            location=params.location,
            source=params.source,
            skill=params.skill,
            min_salary=params.min_salary,
            sort_by=params.sort_by,
            skip=skip,
            limit=params.page_size,
        )

        total_pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0

        items = [self._to_response(j) for j in jobs]
        return JobListResponse(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )

    # Alias per specification
    searchJobs = search_jobs

    async def get_job(self, job_id: Union[uuid.UUID, str]) -> Optional[JobResponse]:
        """
        Retrieves a single job with its associated skills by UUID.
        """
        job = await self.repository.find_by_id(job_id)
        if not job:
            return None
        return self._to_response(job)

    # Alias per specification
    getJob = get_job

    async def extract_skills(self, description: str, seed_skills: Optional[List[str]] = None) -> List[str]:
        """
        Direct access to skill extraction for job descriptions.
        """
        return await self.skill_extractor.extract_skills(description, seed_skills)

    # Alias per specification
    extractSkills = extract_skills

    def _to_response(self, job: JobModel) -> JobResponse:
        skill_names = [s.skill_name for s in getattr(job, "skills", [])]
        return JobResponse(
            id=job.id,
            source=job.source,
            external_id=job.external_id,
            title=job.title,
            company=job.company,
            location=job.location,
            employment_type=job.employment_type,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            currency=job.currency or "USD",
            description=job.description,
            requirements=job.requirements,
            apply_url=job.apply_url,
            company_website=job.company_website,
            posted_at=job.posted_at,
            created_at=job.created_at,
            updated_at=job.updated_at,
            skills=skill_names,
        )
