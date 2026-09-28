import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.application import ApplicationModel
from models.job import JobModel
from models.match_result import MatchResultModel
from models.profile import ProfileModel
from models.report import ReportModel
from models.resume import ResumeModel
from models.skill import SkillModel
from models.user import UserModel
from services.webhook_service import WebhookService


class PublicApiService:
    """
    Service layer providing clean, sanitized domain data access for the versioned Public API (/api/public/v1/*).
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.webhook_service = WebhookService(session)

    async def get_profile(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        stmt = (
            select(UserModel)
            .where(UserModel.id == user_id)
            .options(
                selectinload(UserModel.profile),
                selectinload(UserModel.skills),
            )
        )
        res = await self.session.execute(stmt)
        user = res.scalars().first()
        if not user:
            return None

        skills_list = [s.name for s in (user.skills or [])]
        prof = user.profile

        return {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "summary": prof.summary if prof else None,
            "preferred_roles": prof.preferred_roles if prof else [],
            "preferred_locations": prof.preferred_locations if prof else [],
            "years_of_experience": prof.years_of_experience if prof else 0,
            "skills": skills_list,
        }

    async def list_resumes(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        stmt = (
            select(ResumeModel)
            .where(ResumeModel.user_id == user_id)
            .order_by(desc(ResumeModel.uploaded_at))
        )
        res = await self.session.execute(stmt)
        resumes = res.scalars().all()

        # Fetch candidate skills
        skills_stmt = select(SkillModel).where(SkillModel.user_id == user_id)
        s_res = await self.session.execute(skills_stmt)
        skill_names = [s.name for s in s_res.scalars().all()]

        return [
            {
                "id": r.id,
                "user_id": r.user_id,
                "filename": r.original_filename,
                "file_type": r.file_type,
                "file_size": r.file_size,
                "uploaded_at": r.uploaded_at,
                "skills": skill_names,
            }
            for r in resumes
        ]

    async def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        stmt = select(ResumeModel).where(
            ResumeModel.id == resume_id,
            ResumeModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        r = res.scalars().first()
        if not r:
            return None

        skills_stmt = select(SkillModel).where(SkillModel.user_id == user_id)
        s_res = await self.session.execute(skills_stmt)
        skill_names = [s.name for s in s_res.scalars().all()]

        return {
            "id": r.id,
            "user_id": r.user_id,
            "filename": r.original_filename,
            "file_type": r.file_type,
            "file_size": r.file_size,
            "uploaded_at": r.uploaded_at,
            "skills": skill_names,
        }

    async def list_matches(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        stmt = (
            select(MatchResultModel, JobModel)
            .join(JobModel, MatchResultModel.job_id == JobModel.id)
            .where(MatchResultModel.user_id == user_id)
            .order_by(desc(MatchResultModel.overall_score))
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(MatchResultModel)
            .where(MatchResultModel.user_id == user_id)
        )

        rows = await self.session.execute(stmt)
        count_res = await self.session.execute(count_stmt)

        items = []
        for match, job in rows.all():
            items.append({
                "id": match.id,
                "job_id": job.id,
                "job_title": job.title,
                "company": job.company,
                "location": job.location,
                "overall_score": match.overall_score,
                "skill_score": match.skill_score,
                "experience_score": match.experience_score,
                "strengths": match.strengths or [],
                "missing_skills": match.missing_skills or [],
                "recommendations": match.recommendations or [],
                "apply_url": job.apply_url,
            })

        return items, int(count_res.scalar() or 0)

    async def get_match_by_job(self, user_id: uuid.UUID, job_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        stmt = (
            select(MatchResultModel, JobModel)
            .join(JobModel, MatchResultModel.job_id == JobModel.id)
            .where(
                MatchResultModel.user_id == user_id,
                MatchResultModel.job_id == job_id,
            )
        )
        res = await self.session.execute(stmt)
        row = res.first()
        if not row:
            return None
        match, job = row
        return {
            "id": match.id,
            "job_id": job.id,
            "job_title": job.title,
            "company": job.company,
            "location": job.location,
            "overall_score": match.overall_score,
            "skill_score": match.skill_score,
            "experience_score": match.experience_score,
            "strengths": match.strengths or [],
            "missing_skills": match.missing_skills or [],
            "recommendations": match.recommendations or [],
            "apply_url": job.apply_url,
        }

    async def list_applications(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        stmt = (
            select(ApplicationModel)
            .where(ApplicationModel.user_id == user_id)
            .options(selectinload(ApplicationModel.job))
            .order_by(desc(ApplicationModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(ApplicationModel)
            .where(ApplicationModel.user_id == user_id)
        )

        rows = await self.session.execute(stmt)
        count_res = await self.session.execute(count_stmt)

        items = []
        for app in rows.scalars().all():
            items.append({
                "id": app.id,
                "user_id": app.user_id,
                "job_id": app.job_id,
                "job_title": app.job.title if app.job else "Unknown Role",
                "company": app.job.company if app.job else "Unknown Company",
                "status": app.status,
                "applied_at": app.application_date,
                "notes": app.notes,
                "created_at": app.created_at,
                "updated_at": app.last_updated,
            })

        return items, int(count_res.scalar() or 0)

    async def create_application(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        resume_id: Optional[uuid.UUID] = None,
        status: str = "Applied",
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        job_res = await self.session.execute(select(JobModel).where(JobModel.id == job_id))
        job = job_res.scalars().first()
        if not job:
            raise ValueError(f"Job not found with id: {job_id}")

        app = ApplicationModel(
            user_id=user_id,
            job_id=job_id,
            tailored_resume_id=resume_id,
            status=status,
            notes=notes,
            application_date=datetime.now(timezone.utc),
        )
        self.session.add(app)
        await self.session.flush()
        await self.session.refresh(app)

        # Dispatch application.created webhook event
        try:
            await self.webhook_service.dispatch_event(
                user_id=user_id,
                event="application.created",
                data={
                    "application_id": str(app.id),
                    "job_id": str(job.id),
                    "job_title": job.title,
                    "company": job.company,
                    "status": app.status,
                },
            )
        except Exception:
            pass

        return {
            "id": app.id,
            "user_id": app.user_id,
            "job_id": app.job_id,
            "job_title": job.title,
            "company": job.company,
            "status": app.status,
            "applied_at": app.application_date,
            "notes": app.notes,
            "created_at": app.created_at,
            "updated_at": app.last_updated,
        }

    async def get_application(self, user_id: uuid.UUID, app_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        stmt = (
            select(ApplicationModel)
            .where(
                ApplicationModel.id == app_id,
                ApplicationModel.user_id == user_id,
            )
            .options(selectinload(ApplicationModel.job))
        )
        res = await self.session.execute(stmt)
        app = res.scalars().first()
        if not app:
            return None

        return {
            "id": app.id,
            "user_id": app.user_id,
            "job_id": app.job_id,
            "job_title": app.job.title if app.job else "Unknown Role",
            "company": app.job.company if app.job else "Unknown Company",
            "status": app.status,
            "applied_at": app.application_date,
            "notes": app.notes,
            "created_at": app.created_at,
            "updated_at": app.last_updated,
        }

    async def list_reports(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        stmt = (
            select(ReportModel)
            .where(ReportModel.user_id == user_id)
            .order_by(desc(ReportModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        count_stmt = (
            select(func.count())
            .select_from(ReportModel)
            .where(ReportModel.user_id == user_id)
        )

        res = await self.session.execute(stmt)
        count_res = await self.session.execute(count_stmt)

        items = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "title": r.title,
                "report_type": r.report_type,
                "format": r.format,
                "file_size_bytes": r.file_size_bytes,
                "created_at": r.created_at,
            }
            for r in res.scalars().all()
        ]
        return items, int(count_res.scalar() or 0)

    async def get_report(self, user_id: uuid.UUID, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        stmt = select(ReportModel).where(
            ReportModel.id == report_id,
            ReportModel.user_id == user_id,
        )
        res = await self.session.execute(stmt)
        r = res.scalars().first()
        if not r:
            return None

        return {
            "id": r.id,
            "user_id": r.user_id,
            "title": r.title,
            "report_type": r.report_type,
            "format": r.format,
            "file_size_bytes": r.file_size_bytes,
            "created_at": r.created_at,
        }
