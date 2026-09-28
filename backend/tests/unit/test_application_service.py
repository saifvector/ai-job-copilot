"""
Unit tests for ApplicationService (Phase 8).
Validates application pipeline tracking, status transitions, interview scheduling,
and conversion analytics.
"""
import uuid
from datetime import datetime, timezone
import pytest
from core.exceptions import BadRequestException, NotFoundException
from models.application import ApplicationModel
from models.job import JobModel
from models.user import UserModel
from repositories.application_event_repository import ApplicationEventRepository
from repositories.application_repository import ApplicationRepository
from repositories.interview_repository import InterviewRepository
from repositories.job_repository import JobRepository
from repositories.user_repository import UserRepository
from schemas.application import (
    ApplicationCreateRequest,
    ApplicationEventCreateRequest,
    InterviewCreateRequest,
)
from services.application_service import ApplicationService


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_create_and_transition_application_status(db_session, mock_user_id):
    """Test full application creation and status lifecycle transition with event logging."""
    user_repo = UserRepository(db_session)
    job_repo = JobRepository(db_session)
    app_repo = ApplicationRepository(db_session)
    event_repo = ApplicationEventRepository(db_session)
    interview_repo = InterviewRepository(db_session)

    service = ApplicationService(
        application_repo=app_repo,
        event_repo=event_repo,
        interview_repo=interview_repo,
        job_repo=job_repo,
        user_repo=user_repo,
    )

    # 1. Create a test job
    job = JobModel(
        id=uuid.uuid4(),
        source="Wellfound",
        external_id=f"wf-test-{uuid.uuid4().hex[:8]}",
        title="Senior Platform Engineer",
        company="Datadog Partner",
        location="Remote",
        description="Scalable distributed platform engineering.",
        apply_url="https://example.com/apply/wf1",
    )
    db_session.add(job)
    await db_session.flush()

    # 2. Track as SAVED
    create_req = ApplicationCreateRequest(
        job_id=job.id,
        status="SAVED",
        source="Wellfound",
        notes="High interest platform role",
    )
    app_res = await service.create_application(user_id=mock_user_id, request=create_req)

    assert app_res.status == "SAVED"
    assert app_res.job is not None
    assert app_res.job.title == "Senior Platform Engineer"
    assert len(app_res.events) >= 1
    assert app_res.events[0].event_type == "CREATED"

    # 3. Transition to APPLIED
    updated_res = await service.update_status(
        application_id=app_res.id,
        new_status="APPLIED",
        notes="Submitted resume version A via portal",
    )
    assert updated_res.status == "APPLIED"
    assert updated_res.application_date is not None
    # Check that events list now contains STATUS_CHANGE
    events = [e.event_type for e in updated_res.events]
    assert "STATUS_CHANGE" in events

    # 4. Schedule Interview
    interview_req = InterviewCreateRequest(
        interview_type="TECHNICAL",
        interview_date=datetime(2026, 10, 15, 14, 0, tzinfo=timezone.utc),
        interview_round=1,
        notes="Prepare system design and concurrency topics",
    )
    interview_res = await service.add_interview(application_id=app_res.id, request=interview_req)
    assert interview_res.interview_type == "TECHNICAL"
    assert interview_res.interview_round == 1

    # Reload application to check auto-advanced status
    app_details = await service.get_application_by_id(app_res.id)
    assert app_details.status == "INTERVIEW"
    assert len(app_details.interviews) == 1


@pytest.mark.asyncio
async def test_pipeline_kanban_grouping(db_session, mock_user_id):
    """Test applications grouping across Kanban pipeline columns."""
    service = ApplicationService(
        application_repo=ApplicationRepository(db_session),
        event_repo=ApplicationEventRepository(db_session),
        interview_repo=InterviewRepository(db_session),
        job_repo=JobRepository(db_session),
        user_repo=UserRepository(db_session),
    )

    # Create 3 jobs in different statuses
    for i, st in enumerate(["SAVED", "APPLIED", "OFFER"]):
        job = JobModel(
            id=uuid.uuid4(),
            source="RemoteOK",
            external_id=f"kanban-job-{i}-{uuid.uuid4().hex[:6]}",
            title=f"Engineer {i}",
            company=f"Company {i}",
            location="Remote",
            description="Testing kanban.",
            apply_url="https://example.com/apply",
        )
        db_session.add(job)
        await db_session.flush()

        await service.create_application(
            user_id=mock_user_id,
            request=ApplicationCreateRequest(job_id=job.id, status=st),
        )

    pipeline = await service.get_pipeline(mock_user_id)
    assert len(pipeline.saved) >= 1
    assert len(pipeline.applied) >= 1
    assert len(pipeline.offer) >= 1
    assert pipeline.total_active >= 3


@pytest.mark.asyncio
async def test_analytics_metrics_calculation(db_session, mock_user_id):
    """Test conversion metrics and interview rate calculation."""
    service = ApplicationService(
        application_repo=ApplicationRepository(db_session),
        event_repo=ApplicationEventRepository(db_session),
        interview_repo=InterviewRepository(db_session),
        job_repo=JobRepository(db_session),
        user_repo=UserRepository(db_session),
    )

    analytics = await service.get_analytics(mock_user_id)
    assert analytics.total_applications >= 0
    assert 0.0 <= analytics.response_rate <= 100.0
    assert 0.0 <= analytics.interview_rate <= 100.0
    assert 0.0 <= analytics.offer_rate <= 100.0
    assert "SAVED" in analytics.by_status
    assert "OFFER" in analytics.by_status
