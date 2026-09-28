"""
Candidate Intelligence Repositories for Phase 3 Resume Parsing.
Provides dedicated query capabilities for Skill, Project, Education, Experience, and Certification entities.
"""
import uuid
from typing import List, Union
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.certification import CertificationModel
from models.education import EducationModel
from models.experience import ExperienceModel
from models.project import ProjectModel
from models.skill import SkillModel
from repositories.base import BaseRepository


class SkillRepository(BaseRepository[SkillModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SkillModel, session)

    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> List[SkillModel]:
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(SkillModel)
            .where(SkillModel.user_id == uid)
            .order_by(SkillModel.category, SkillModel.confidence_score.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: Union[uuid.UUID, str]) -> int:
        uid = uuid.UUID(str(user_id))
        stmt = delete(SkillModel).where(SkillModel.user_id == uid)
        result = await self.session.execute(stmt)
        return result.rowcount or 0


class ProjectRepository(BaseRepository[ProjectModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ProjectModel, session)

    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> List[ProjectModel]:
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(ProjectModel)
            .where(ProjectModel.user_id == uid)
            .order_by(ProjectModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: Union[uuid.UUID, str]) -> int:
        uid = uuid.UUID(str(user_id))
        stmt = delete(ProjectModel).where(ProjectModel.user_id == uid)
        result = await self.session.execute(stmt)
        return result.rowcount or 0


class EducationRepository(BaseRepository[EducationModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(EducationModel, session)

    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> List[EducationModel]:
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(EducationModel)
            .where(EducationModel.user_id == uid)
            .order_by(EducationModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: Union[uuid.UUID, str]) -> int:
        uid = uuid.UUID(str(user_id))
        stmt = delete(EducationModel).where(EducationModel.user_id == uid)
        result = await self.session.execute(stmt)
        return result.rowcount or 0


class ExperienceRepository(BaseRepository[ExperienceModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ExperienceModel, session)

    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> List[ExperienceModel]:
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(ExperienceModel)
            .where(ExperienceModel.user_id == uid)
            .order_by(ExperienceModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: Union[uuid.UUID, str]) -> int:
        uid = uuid.UUID(str(user_id))
        stmt = delete(ExperienceModel).where(ExperienceModel.user_id == uid)
        result = await self.session.execute(stmt)
        return result.rowcount or 0


class CertificationRepository(BaseRepository[CertificationModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(CertificationModel, session)

    async def get_by_user_id(self, user_id: Union[uuid.UUID, str]) -> List[CertificationModel]:
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(CertificationModel)
            .where(CertificationModel.user_id == uid)
            .order_by(CertificationModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: Union[uuid.UUID, str]) -> int:
        uid = uuid.UUID(str(user_id))
        stmt = delete(CertificationModel).where(CertificationModel.user_id == uid)
        result = await self.session.execute(stmt)
        return result.rowcount or 0
