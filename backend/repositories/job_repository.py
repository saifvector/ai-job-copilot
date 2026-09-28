import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.job import JobModel
from models.job_skill import JobSkillModel
from repositories.base import BaseRepository


class JobRepository(BaseRepository[JobModel]):
    """
    Repository for managing Job entities and extracted JobSkills in PostgreSQL.
    Methods: create, update, search, findById, findByExternalId.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(JobModel, session)

    async def create_job(
        self,
        job_data: Dict[str, Any],
        skills: List[str] | None = None,
    ) -> JobModel:
        """
        Creates a Job record and its associated JobSkill records atomically.
        """
        job = JobModel(**job_data)
        self.session.add(job)
        await self.session.flush()

        if skills:
            seen_skills = set()
            for skill_name in skills:
                name_clean = skill_name.strip()
                if name_clean and name_clean.lower() not in seen_skills:
                    seen_skills.add(name_clean.lower())
                    skill_obj = JobSkillModel(
                        job_id=job.id,
                        skill_name=name_clean,
                    )
                    self.session.add(skill_obj)
            await self.session.flush()

        await self.session.refresh(job)
        return job

    # Alias per specification
    create = create_job

    async def update_job(
        self,
        job_id: Union[uuid.UUID, str],
        job_data: Dict[str, Any],
    ) -> Optional[JobModel]:
        """
        Updates an existing Job record.
        """
        job = await self.get_by_id(job_id)
        if not job:
            return None
        for key, value in job_data.items():
            if hasattr(job, key):
                setattr(job, key, value)
        self.session.add(job)
        await self.session.flush()
        await self.session.refresh(job)
        return job

    # Alias per specification
    update = update_job

    async def find_by_id(self, job_id: Union[uuid.UUID, str]) -> Optional[JobModel]:
        """
        Finds a Job by UUID with its skills eagerly loaded.
        """
        if isinstance(job_id, str):
            try:
                job_id = uuid.UUID(job_id)
            except ValueError:
                return None

        stmt = (
            select(JobModel)
            .where(JobModel.id == job_id)
            .options(selectinload(JobModel.skills))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Exact camelCase method requested in requirements
    findById = find_by_id

    async def find_by_external_id(self, source: str, external_id: str) -> Optional[JobModel]:
        """
        Finds a Job by source and external ID.
        """
        stmt = (
            select(JobModel)
            .where(JobModel.source == source, JobModel.external_id == external_id)
            .options(selectinload(JobModel.skills))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # Exact camelCase method requested in requirements
    findByExternalId = find_by_external_id

    async def find_by_deduplication_key(
        self,
        company: str,
        title: str,
        apply_url: str,
    ) -> Optional[JobModel]:
        """
        Checks for an existing job by matching company, title, or apply_url.
        """
        stmt = (
            select(JobModel)
            .where(
                or_(
                    func.lower(JobModel.apply_url) == apply_url.lower().rstrip("/"),
                    (
                        func.lower(JobModel.company) == company.lower().strip()
                    ) & (
                        func.lower(JobModel.title) == title.lower().strip()
                    ),
                )
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(
        self,
        query: Optional[str] = None,
        role: Optional[str] = None,
        location: Optional[str] = None,
        source: Optional[str] = None,
        skill: Optional[str] = None,
        min_salary: Optional[float] = None,
        sort_by: str = "newest",
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[JobModel], int]:
        """
        Searches jobs using dynamic multi-criteria filters, skill joins, and sorting.
        Returns: (jobs_list, total_count)
        """
        stmt = select(JobModel).options(selectinload(JobModel.skills))
        count_stmt = select(func.count(func.distinct(JobModel.id))).select_from(JobModel)

        conditions = []

        # Free text query across title, company, description
        if query and query.strip():
            q = f"%{query.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(JobModel.title).like(q),
                    func.lower(JobModel.company).like(q),
                    func.lower(JobModel.description).like(q),
                )
            )

        # Role / Title filter
        if role and role.strip():
            r = f"%{role.strip().lower()}%"
            conditions.append(func.lower(JobModel.title).like(r))

        # Location filter
        if location and location.strip():
            loc = f"%{location.strip().lower()}%"
            conditions.append(func.lower(JobModel.location).like(loc))

        # Source filter
        if source and source.strip():
            conditions.append(func.lower(JobModel.source) == source.strip().lower())

        # Minimum salary filter
        if min_salary is not None and min_salary > 0:
            conditions.append(
                or_(
                    JobModel.salary_max >= min_salary,
                    JobModel.salary_min >= min_salary,
                )
            )

        # Skill filter: join JobSkillModel
        if skill and skill.strip():
            stmt = stmt.join(JobSkillModel, JobSkillModel.job_id == JobModel.id)
            count_stmt = count_stmt.join(JobSkillModel, JobSkillModel.job_id == JobModel.id)
            conditions.append(func.lower(JobSkillModel.skill_name) == skill.strip().lower())

        if conditions:
            stmt = stmt.where(*conditions)
            count_stmt = count_stmt.where(*conditions)

        # Total count query
        count_res = await self.session.execute(count_stmt)
        total_count = count_res.scalar_one() or 0

        # Sorting
        if sort_by == "highest_salary":
            stmt = stmt.order_by(JobModel.salary_max.desc().nullslast(), JobModel.salary_min.desc().nullslast())
        elif sort_by == "most_relevant":
            stmt = stmt.order_by(JobModel.posted_at.desc().nullslast(), JobModel.created_at.desc())
        else:  # 'newest' default
            stmt = stmt.order_by(JobModel.posted_at.desc().nullslast(), JobModel.created_at.desc())

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.session.execute(stmt)
        # Unique scalars because of possible joins
        jobs = list(result.scalars().unique().all())

        return jobs, total_count
