"""
Unit tests for InterviewService (Phase 11 AI Interview Preparation Platform).
Covers question generation, answer evaluation, mock interview sessions,
career coaching, and analytics.
"""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.candidate_intelligence_repository import (
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.interview_repository import (
    InterviewPreparationRepository,
    MockInterviewRepository,
    QuestionRepository,
)
from repositories.job_repository import JobRepository
from repositories.user_repository import UserRepository
from schemas.interview import (
    AnswerEvaluationRequest,
    QuestionGenerateRequest,
)
from services.interview_service import InterviewService


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.fixture
def interview_service(db_session: AsyncSession) -> InterviewService:
    prep_repo = InterviewPreparationRepository(session=db_session)
    question_repo = QuestionRepository(session=db_session)
    mock_repo = MockInterviewRepository(session=db_session)
    user_repo = UserRepository(session=db_session)
    job_repo = JobRepository(session=db_session)
    skill_repo = SkillRepository(session=db_session)
    project_repo = ProjectRepository(session=db_session)
    experience_repo = ExperienceRepository(session=db_session)

    return InterviewService(
        prep_repo=prep_repo,
        question_repo=question_repo,
        mock_repo=mock_repo,
        user_repo=user_repo,
        job_repo=job_repo,
        skill_repo=skill_repo,
        project_repo=project_repo,
        experience_repo=experience_repo,
    )


@pytest.mark.asyncio
async def test_generate_interview_questions(interview_service: InterviewService, mock_user_id: uuid.UUID):
    """Test generating personalized interview questions with resume/project grounding."""
    request = QuestionGenerateRequest(
        role="Staff Machine Learning Engineer",
        preparationType="Comprehensive",
        questionCount=8,
    )

    result = await interview_service.generate_questions(user_id=mock_user_id, request=request)

    assert result.role == "Staff Machine Learning Engineer"
    assert result.total_questions >= 8
    assert result.completed_questions == 0
    assert len(result.questions) >= 8

    # Verify category diversity
    categories = {q.category for q in result.questions}
    assert "Project-Based" in categories or "Resume-Based" in categories or "Technical" in categories
    assert any("Brain Tumor" in q.question or "architecture" in q.question.lower() or "model" in q.question.lower() for q in result.questions)

    # Verify difficulty coverage
    difficulties = {q.difficulty for q in result.questions}
    assert "Medium" in difficulties or "Hard" in difficulties or "Easy" in difficulties


@pytest.mark.asyncio
async def test_evaluate_candidate_answer(interview_service: InterviewService, mock_user_id: uuid.UUID):
    """Test answer evaluation engine scoring and feedback."""
    # 1. Generate a question first to have a valid ID
    prep_res = await interview_service.generate_questions(
        user_id=mock_user_id,
        request=QuestionGenerateRequest(role="Senior Backend Engineer", questionCount=4),
    )
    first_question = prep_res.questions[0]

    # 2. Evaluate answer
    eval_req = AnswerEvaluationRequest(
        questionId=first_question.id,
        userAnswer=(
            "In my previous project, we faced high latency under concurrent spikes. "
            "I was responsible for optimizing the throughput. "
            "I implemented an LRU Redis cache-aside layer with write-through invalidation and database indexing on PostgreSQL, "
            "which reduced latency by 68% and achieved 12,000 requests per second."
        ),
        category=first_question.category,
        difficulty=first_question.difficulty,
        role="Senior Backend Engineer",
    )

    eval_result = await interview_service.evaluate_answer(user_id=mock_user_id, request=eval_req)

    assert eval_result.score >= 60.0
    assert len(eval_result.strengths) > 0
    assert len(eval_result.suggested_improvements) > 0
    assert len(eval_result.feedback) > 0

    # 3. Verify question status is marked completed in DB
    updated_questions = await interview_service.get_questions(user_id=mock_user_id, is_completed=True)
    assert any(q.id == first_question.id for q in updated_questions)


@pytest.mark.asyncio
async def test_mock_interview_session(interview_service: InterviewService, mock_user_id: uuid.UUID):
    """Test completing a multi-question mock interview session."""
    answers = [
        {
            "question": "How do you scale a microservice architecture?",
            "userAnswer": "By implementing stateless API gateways, horizontal pod autoscaling with Kubernetes, distributed Redis caching, and Kafka event streaming.",
            "category": "System Design",
            "difficulty": "Hard",
        },
        {
            "question": "Tell me about a challenge you overcame.",
            "userAnswer": "When database deadlocks occurred during high traffic, I led an emergency incident response, reorganized table lock ordering, and deployed a zero-downtime hotfix.",
            "category": "Behavioral",
            "difficulty": "Medium",
        },
    ]

    mock_res = await interview_service.generate_mock_interview(
        user_id=mock_user_id,
        role="Principal Distributed Systems Architect",
        answers=answers,
    )

    assert mock_res.role == "Principal Distributed Systems Architect"
    assert mock_res.score > 50.0
    assert "summary" in mock_res.feedback
    assert len(mock_res.feedback["questionBreakdown"]) == 2

    # Check history
    history = await interview_service.get_interview_history(user_id=mock_user_id)
    assert history["totalSessions"] >= 1


@pytest.mark.asyncio
async def test_career_coaching_and_roadmap(interview_service: InterviewService, mock_user_id: uuid.UUID):
    """Test generating career coaching insights, readiness score, and 4-week learning roadmap."""
    coaching = await interview_service.generate_roadmap(
        user_id=mock_user_id,
        role="Senior AI Application Engineer",
    )

    assert coaching.role == "Senior AI Application Engineer"
    assert 35.0 <= coaching.interview_readiness_score <= 100.0
    assert len(coaching.strong_areas) > 0
    assert len(coaching.weak_areas) > 0
    assert len(coaching.skill_development_recommendations) >= 3
    assert len(coaching.learning_roadmap) == 4

    # Verify roadmap structure
    weeks = [step["phase"] for step in coaching.learning_roadmap]
    assert "Week 1" in weeks
    assert "Week 2" in weeks
    assert "Week 3" in weeks
    assert "Week 4" in weeks


@pytest.mark.asyncio
async def test_interview_analytics(interview_service: InterviewService, mock_user_id: uuid.UUID):
    """Test candidate interview analytics calculation."""
    analytics = await interview_service.get_analytics(user_id=mock_user_id)

    assert analytics.questions_completed >= 0
    assert analytics.average_score >= 0.0
    assert len(analytics.weak_areas) > 0
    assert len(analytics.strong_areas) > 0
    assert analytics.readiness_score > 0.0
    assert isinstance(analytics.category_breakdown, dict)
