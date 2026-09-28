"""
Interview Repositories for Phase 11 AI Interview Preparation Platform.
Provides database access for InterviewPreparation, Question, and MockInterview entities.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.application import ApplicationModel
from models.interview import InterviewModel
from models.interview_preparation import InterviewPreparationModel
from models.interview_question import QuestionModel
from models.mock_interview import MockInterviewModel
from repositories.base import BaseRepository


class InterviewRepository(BaseRepository[InterviewModel]):
    """
    Repository for Phase 8 application interview scheduling.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(InterviewModel, session)

    async def create(self, data: Dict[str, Any]) -> InterviewModel:
        interview = InterviewModel(**data)
        self.session.add(interview)
        await self.session.flush()
        return interview

    async def list_by_application(self, application_id: Union[uuid.UUID, str]) -> List[InterviewModel]:
        aid = uuid.UUID(str(application_id))
        stmt = (
            select(InterviewModel)
            .where(InterviewModel.application_id == aid)
            .order_by(InterviewModel.interview_round.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def getUpcomingByUser(self, user_id: Union[uuid.UUID, str]) -> List[InterviewModel]:
        """Fetch all upcoming interviews for candidate across all job applications."""
        uid = uuid.UUID(str(user_id))
        now = datetime.now(timezone.utc)
        stmt = (
            select(InterviewModel)
            .join(ApplicationModel, InterviewModel.application_id == ApplicationModel.id)
            .where(
                ApplicationModel.user_id == uid,
                InterviewModel.interview_date >= now,
            )
            .order_by(InterviewModel.interview_date.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class InterviewPreparationRepository(BaseRepository[InterviewPreparationModel]):
    """
    Repository for InterviewPreparation entity.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(InterviewPreparationModel, session)

    async def create(self, data: Dict[str, Any]) -> InterviewPreparationModel:
        """Create a new InterviewPreparation entity."""
        prep = InterviewPreparationModel(**data)
        self.session.add(prep)
        await self.session.flush()
        return prep

    async def findById(
        self,
        prep_id: Union[uuid.UUID, str],
        eager: bool = True,
    ) -> Optional[InterviewPreparationModel]:
        """Find preparation by ID with optional eager loading of questions."""
        p_id = uuid.UUID(str(prep_id))
        stmt = select(InterviewPreparationModel).where(InterviewPreparationModel.id == p_id)
        if eager:
            stmt = stmt.options(
                selectinload(InterviewPreparationModel.questions),
                selectinload(InterviewPreparationModel.job),
            )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 50,
        offset: int = 0,
    ) -> List[InterviewPreparationModel]:
        """List preparations for a specific candidate ordered by most recent."""
        u_id = uuid.UUID(str(user_id))
        stmt = (
            select(InterviewPreparationModel)
            .where(InterviewPreparationModel.user_id == u_id)
            .options(
                selectinload(InterviewPreparationModel.questions),
                selectinload(InterviewPreparationModel.job),
            )
            .order_by(desc(InterviewPreparationModel.generated_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, prep_id: Union[uuid.UUID, str]) -> bool:
        """Delete an interview preparation set and cascade delete questions."""
        prep = await self.findById(prep_id, eager=False)
        if not prep:
            return False
        await self.session.delete(prep)
        await self.session.flush()
        return True


class QuestionRepository(BaseRepository[QuestionModel]):
    """
    Repository for Question entity.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(QuestionModel, session)

    async def create(self, data: Dict[str, Any]) -> QuestionModel:
        """Create a new Question entity."""
        question = QuestionModel(**data)
        self.session.add(question)
        await self.session.flush()
        return question

    async def create_batch(self, questions_data: List[Dict[str, Any]]) -> List[QuestionModel]:
        """Create multiple questions in a single flush."""
        created: List[QuestionModel] = []
        for q_data in questions_data:
            q = QuestionModel(**q_data)
            self.session.add(q)
            created.append(q)
        await self.session.flush()
        return created

    async def findById(
        self,
        question_id: Union[uuid.UUID, str],
    ) -> Optional[QuestionModel]:
        """Find question by ID."""
        q_id = uuid.UUID(str(question_id))
        stmt = select(QuestionModel).where(QuestionModel.id == q_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_preparation(
        self,
        preparation_id: Union[uuid.UUID, str],
    ) -> List[QuestionModel]:
        """List all questions belonging to an interview preparation set."""
        p_id = uuid.UUID(str(preparation_id))
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.preparation_id == p_id)
            .order_by(QuestionModel.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_completed: Optional[bool] = None,
        preparation_id: Optional[Union[uuid.UUID, str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[QuestionModel]:
        """
        List candidate questions across all or specific preparations with filtering.
        """
        u_id = uuid.UUID(str(user_id))
        stmt = (
            select(QuestionModel)
            .join(InterviewPreparationModel, QuestionModel.preparation_id == InterviewPreparationModel.id)
            .where(InterviewPreparationModel.user_id == u_id)
        )

        conditions = []
        if preparation_id:
            conditions.append(QuestionModel.preparation_id == uuid.UUID(str(preparation_id)))
        if category and category.lower() != "all":
            conditions.append(QuestionModel.category == category)
        if difficulty and difficulty.lower() != "all":
            conditions.append(QuestionModel.difficulty == difficulty)
        if is_completed is not None:
            conditions.append(QuestionModel.is_completed == is_completed)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(desc(QuestionModel.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_evaluation(
        self,
        question: QuestionModel,
        user_answer: str,
        score: float,
        feedback: str,
    ) -> QuestionModel:
        """Record candidate answer evaluation and mark completed."""
        question.user_answer = user_answer
        question.score = score
        question.feedback = feedback
        question.is_completed = True
        question.evaluated_at = datetime.now(timezone.utc)
        question.updated_at = datetime.now(timezone.utc)
        self.session.add(question)
        await self.session.flush()
        return question


class MockInterviewRepository(BaseRepository[MockInterviewModel]):
    """
    Repository for MockInterview entity.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MockInterviewModel, session)

    async def create(self, data: Dict[str, Any]) -> MockInterviewModel:
        """Create a new MockInterview session record."""
        session = MockInterviewModel(**data)
        self.session.add(session)
        await self.session.flush()
        return session

    async def findById(
        self,
        session_id: Union[uuid.UUID, str],
    ) -> Optional[MockInterviewModel]:
        """Find mock interview session by ID."""
        s_id = uuid.UUID(str(session_id))
        stmt = select(MockInterviewModel).where(MockInterviewModel.id == s_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 50,
        offset: int = 0,
    ) -> List[MockInterviewModel]:
        """List mock interview sessions for user ordered by newest."""
        u_id = uuid.UUID(str(user_id))
        stmt = (
            select(MockInterviewModel)
            .where(MockInterviewModel.user_id == u_id)
            .order_by(desc(MockInterviewModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
