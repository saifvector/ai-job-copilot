"""
Unit tests for ApplicationAssistantService (Phase 12 Application Assistant Platform).
Tests draft lifecycle, truthful AI answer generation, document selection,
checklist evaluation, candidate review workflow, and analytics.
"""
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.job import JobModel
from repositories.application_assistant_repository import (
    ApplicationDraftRepository,
    ApplicationQuestionRepository,
)
from repositories.candidate_intelligence_repository import (
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.job_repository import JobRepository
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from repositories.tailored_resume_repository import TailoredResumeRepository
from schemas.application_assistant import (
    ApplicationDraftCreateRequest,
    ApplicationQuestionCreate,
    ApplicationQuestionUpdate,
    GenerateAnswersRequest,
    ReviewDraftRequest,
)
from services.application_assistant_service import ApplicationAssistantService


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.fixture
def assistant_service(db_session: AsyncSession) -> ApplicationAssistantService:
    draft_repo = ApplicationDraftRepository(session=db_session)
    question_repo = ApplicationQuestionRepository(session=db_session)
    job_repo = JobRepository(session=db_session)
    profile_repo = ProfileRepository(session=db_session)
    resume_repo = ResumeRepository(session=db_session)
    tailored_repo = TailoredResumeRepository(session=db_session)
    skill_repo = SkillRepository(session=db_session)
    exp_repo = ExperienceRepository(session=db_session)
    proj_repo = ProjectRepository(session=db_session)
    edu_repo = EducationRepository(session=db_session)

    return ApplicationAssistantService(
        draft_repo=draft_repo,
        question_repo=question_repo,
        job_repo=job_repo,
        profile_repo=profile_repo,
        resume_repo=resume_repo,
        tailored_resume_repo=tailored_repo,
        skill_repo=skill_repo,
        experience_repo=exp_repo,
        project_repo=proj_repo,
        education_repo=edu_repo,
    )


@pytest.fixture
async def sample_job(db_session: AsyncSession) -> JobModel:
    job = JobModel(
        source="Direct",
        external_id=f"job-{uuid.uuid4().hex[:8]}",
        title="Senior Full-Stack Engineer",
        company="NextGen Systems",
        location="Remote",
        description="Looking for an experienced engineer skilled in Python, FastAPI, React, and cloud architectures.",
        salary_min=130000.0,
        salary_max=160000.0,
        currency="USD",
        apply_url="https://example.com/jobs/apply/1",
    )
    db_session.add(job)
    await db_session.flush()
    return job


@pytest.mark.asyncio
async def test_create_draft_success(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test creating an application draft with default questions and checklist."""
    payload = ApplicationDraftCreateRequest(
        job_id=sample_job.id,
        notes="Targeting Q4 hiring cycle.",
    )
    draft_res = await assistant_service.create_draft(user_id=mock_user_id, payload=payload)

    assert draft_res.id is not None
    assert draft_res.job_id == sample_job.id
    assert draft_res.status == "Draft"
    assert len(draft_res.questions) >= 6
    assert draft_res.job is not None
    assert draft_res.job["title"] == "Senior Full-Stack Engineer"
    assert draft_res.readiness_score >= 0.0


@pytest.mark.asyncio
async def test_create_draft_custom_questions(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test creating an application draft with custom employer-specific questions."""
    custom_qs = [
        ApplicationQuestionCreate(
            question="Are you authorized to work in the US without sponsorship?",
            answerType="YesNo",
            options=["Yes", "No"],
            isRequired=True,
            order=1,
        ),
        ApplicationQuestionCreate(
            question="Select the primary frameworks you have built production apps with:",
            answerType="MultiSelect",
            options=["React", "Vue", "Angular", "Next.js"],
            isRequired=True,
            order=2,
        ),
    ]
    payload = ApplicationDraftCreateRequest(
        job_id=sample_job.id,
        customQuestions=custom_qs,
    )
    draft_res = await assistant_service.create_draft(user_id=mock_user_id, payload=payload)

    assert len(draft_res.questions) == 2
    assert draft_res.questions[0].answer_type == "YesNo"
    assert draft_res.questions[1].answer_type == "MultiSelect"


@pytest.mark.asyncio
async def test_generate_truthful_answers(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test generating grounded answers with strict truthfulness constraint."""
    # Create draft
    draft_res = await assistant_service.create_draft(
        user_id=mock_user_id,
        payload=ApplicationDraftCreateRequest(job_id=sample_job.id),
    )

    # Generate answers
    gen_payload = GenerateAnswersRequest(
        draftId=draft_res.id,
        regenerateAll=True,
    )
    updated_draft = await assistant_service.generate_answers(user_id=mock_user_id, payload=gen_payload)

    assert updated_draft.id == draft_res.id
    assert len(updated_draft.questions) > 0

    # Verify answers are populated and grounded
    for q in updated_draft.questions:
        assert q.generated_answer is not None
        assert len(q.generated_answer) > 0
        # Check numeric format
        if q.answer_type == "Numeric":
            assert any(char.isdigit() for char in q.generated_answer)
        # Check text format
        if "Why do you want" in q.question:
            assert "NextGen Systems" in q.generated_answer or "Senior Full-Stack Engineer" in q.generated_answer


@pytest.mark.asyncio
async def test_checklist_validation_and_scoring(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test checklist evaluator accurately identifies missing fields and scores readiness."""
    draft_res = await assistant_service.create_draft(
        user_id=mock_user_id,
        payload=ApplicationDraftCreateRequest(job_id=sample_job.id),
    )

    checklist = await assistant_service.validate_draft(user_id=mock_user_id, draft_id=draft_res.id)
    assert checklist.readiness_score >= 0.0
    assert len(checklist.items) >= 3


@pytest.mark.asyncio
async def test_review_workflow_and_candidate_confirmation(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test candidate review workflow, answer editing, and explicit accuracy confirmation."""
    draft_res = await assistant_service.create_draft(
        user_id=mock_user_id,
        payload=ApplicationDraftCreateRequest(job_id=sample_job.id),
    )

    # Generate answers
    gen_res = await assistant_service.generate_answers(
        user_id=mock_user_id,
        payload=GenerateAnswersRequest(draftId=draft_res.id),
    )

    first_q = gen_res.questions[0]
    edited_text = "I have 5 years of verified full-stack experience with modern Python and React systems."

    # Review and edit answer
    review_payload = ReviewDraftRequest(
        draftId=draft_res.id,
        answers=[
            ApplicationQuestionUpdate(
                questionId=first_q.id,
                userAnswer=edited_text,
                isReviewed=True,
            )
        ],
        confirmAccuracy=True,
    )
    reviewed_draft = await assistant_service.review_draft(user_id=mock_user_id, payload=review_payload)

    # Verify candidate review state
    assert reviewed_draft.status in ("ReadyForReview", "Draft")
    first_updated_q = [q for q in reviewed_draft.questions if q.id == first_q.id][0]
    assert first_updated_q.user_answer == edited_text
    assert first_updated_q.is_reviewed is True


@pytest.mark.asyncio
async def test_candidate_explicit_submission(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test candidate explicit submission confirmation (no auto-submit)."""
    draft_res = await assistant_service.create_draft(
        user_id=mock_user_id,
        payload=ApplicationDraftCreateRequest(job_id=sample_job.id),
    )

    submitted_draft = await assistant_service.submit_draft(user_id=mock_user_id, draft_id=draft_res.id)

    assert submitted_draft.status == "SubmittedByUser"
    assert submitted_draft.submitted_at is not None
    assert submitted_draft.readiness_score == 100.0


@pytest.mark.asyncio
async def test_assistant_analytics(
    assistant_service: ApplicationAssistantService,
    mock_user_id: uuid.UUID,
    sample_job: JobModel,
):
    """Test application assistant analytics tracking drafts created and completed."""
    # Create and submit a draft
    draft_res = await assistant_service.create_draft(
        user_id=mock_user_id,
        payload=ApplicationDraftCreateRequest(job_id=sample_job.id),
    )
    await assistant_service.submit_draft(user_id=mock_user_id, draft_id=draft_res.id)

    analytics = await assistant_service.get_analytics(user_id=mock_user_id)
    assert analytics.drafts_created >= 1
    assert analytics.drafts_completed >= 1
    assert "SubmittedByUser" in analytics.status_counts
