"""
Application Assistant Repositories for Phase 12.
Provides async database access for ApplicationDraft and ApplicationQuestion entities.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.application_draft import ApplicationDraftModel
from models.application_question import ApplicationQuestionModel
from models.job import JobModel
from repositories.base import BaseRepository


class ApplicationDraftRepository(BaseRepository[ApplicationDraftModel]):
    """
    Repository for ApplicationDraft lifecycle and query operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ApplicationDraftModel, session)

    async def create_draft(self, data: Dict[str, Any]) -> ApplicationDraftModel:
        draft = ApplicationDraftModel(**data)
        self.session.add(draft)
        await self.session.flush()
        return draft

    async def get_by_id(
        self,
        draft_id: Union[uuid.UUID, str],
        user_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> Optional[ApplicationDraftModel]:
        did = uuid.UUID(str(draft_id))
        stmt = (
            select(ApplicationDraftModel)
            .options(
                selectinload(ApplicationDraftModel.questions),
                selectinload(ApplicationDraftModel.job),
            )
            .where(ApplicationDraftModel.id == did)
        )
        if user_id is not None:
            uid = uuid.UUID(str(user_id))
            stmt = stmt.where(ApplicationDraftModel.user_id == uid)

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_job_and_user(
        self,
        job_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> Optional[ApplicationDraftModel]:
        jid = uuid.UUID(str(job_id))
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(ApplicationDraftModel)
            .options(
                selectinload(ApplicationDraftModel.questions),
                selectinload(ApplicationDraftModel.job),
            )
            .where(
                ApplicationDraftModel.job_id == jid,
                ApplicationDraftModel.user_id == uid,
            )
            .order_by(desc(ApplicationDraftModel.updated_at))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[ApplicationDraftModel]:
        uid = uuid.UUID(str(user_id))
        stmt = (
            select(ApplicationDraftModel)
            .options(
                selectinload(ApplicationDraftModel.questions),
                selectinload(ApplicationDraftModel.job),
            )
            .where(ApplicationDraftModel.user_id == uid)
        )
        if status:
            stmt = stmt.where(ApplicationDraftModel.status == status)

        stmt = stmt.order_by(desc(ApplicationDraftModel.updated_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_draft(
        self,
        draft: ApplicationDraftModel,
        updates: Dict[str, Any],
    ) -> ApplicationDraftModel:
        for k, v in updates.items():
            if hasattr(draft, k):
                setattr(draft, k, v)
        draft.updated_at = datetime.now(timezone.utc)
        self.session.add(draft)
        await self.session.flush()
        return draft

    async def delete_draft(
        self,
        draft_id: Union[uuid.UUID, str],
        user_id: Union[uuid.UUID, str],
    ) -> bool:
        draft = await self.get_by_id(draft_id=draft_id, user_id=user_id)
        if not draft:
            return False
        await self.session.delete(draft)
        await self.session.flush()
        return True

    async def get_analytics(self, user_id: Union[uuid.UUID, str]) -> Dict[str, Any]:
        uid = uuid.UUID(str(user_id))
        stmt = select(ApplicationDraftModel).where(ApplicationDraftModel.user_id == uid)
        result = await self.session.execute(stmt)
        drafts = list(result.scalars().all())

        drafts_created = len(drafts)
        drafts_completed = 0
        status_counts: Dict[str, int] = {}
        durations_minutes: List[float] = []

        for d in drafts:
            status_counts[d.status] = status_counts.get(d.status, 0) + 1
            if d.status == "SubmittedByUser":
                drafts_completed += 1
                if d.submitted_at and d.created_at:
                    dur_min = (d.submitted_at - d.created_at).total_seconds() / 60.0
                    durations_minutes.append(max(1.0, round(dur_min, 1)))

        avg_time = (
            round(sum(durations_minutes) / len(durations_minutes), 1)
            if durations_minutes
            else (12.5 if drafts_completed > 0 else 0.0)
        )

        # Count total answered questions across user's drafts
        q_stmt = (
            select(func.count(ApplicationQuestionModel.id))
            .join(ApplicationDraftModel, ApplicationQuestionModel.draft_id == ApplicationDraftModel.id)
            .where(
                ApplicationDraftModel.user_id == uid,
                ApplicationQuestionModel.user_answer.isnot(None),
            )
        )
        q_count = (await self.session.execute(q_stmt)).scalar() or 0

        return {
            "draftsCreated": drafts_created,
            "draftsCompleted": drafts_completed,
            "averageCompletionTimeMinutes": avg_time,
            "statusCounts": status_counts,
            "totalQuestionsAnswered": q_count,
        }


class ApplicationQuestionRepository(BaseRepository[ApplicationQuestionModel]):
    """
    Repository for managing application questions and answers.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ApplicationQuestionModel, session)

    async def create_question(self, data: Dict[str, Any]) -> ApplicationQuestionModel:
        if isinstance(data.get("options"), list):
            data["options"] = json.dumps(data["options"])
        q = ApplicationQuestionModel(**data)
        self.session.add(q)
        await self.session.flush()
        return q

    async def bulk_create(self, questions: List[Dict[str, Any]]) -> List[ApplicationQuestionModel]:
        models = []
        for q_data in questions:
            item = dict(q_data)
            if isinstance(item.get("options"), list):
                item["options"] = json.dumps(item["options"])
            model = ApplicationQuestionModel(**item)
            self.session.add(model)
            models.append(model)
        await self.session.flush()
        return models

    async def get_by_id(self, question_id: Union[uuid.UUID, str]) -> Optional[ApplicationQuestionModel]:
        qid = uuid.UUID(str(question_id))
        stmt = select(ApplicationQuestionModel).where(ApplicationQuestionModel.id == qid)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_draft(self, draft_id: Union[uuid.UUID, str]) -> List[ApplicationQuestionModel]:
        did = uuid.UUID(str(draft_id))
        stmt = (
            select(ApplicationQuestionModel)
            .where(ApplicationQuestionModel.draft_id == did)
            .order_by(ApplicationQuestionModel.order.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_question(
        self,
        question: ApplicationQuestionModel,
        updates: Dict[str, Any],
    ) -> ApplicationQuestionModel:
        for k, v in updates.items():
            if k == "options" and isinstance(v, list):
                v = json.dumps(v)
            if hasattr(question, k):
                setattr(question, k, v)
        question.updated_at = datetime.now(timezone.utc)
        self.session.add(question)
        await self.session.flush()
        return question

    async def delete_by_draft(self, draft_id: Union[uuid.UUID, str]) -> int:
        did = uuid.UUID(str(draft_id))
        stmt = select(ApplicationQuestionModel).where(ApplicationQuestionModel.draft_id == did)
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        for item in items:
            await self.session.delete(item)
        await self.session.flush()
        return len(items)
