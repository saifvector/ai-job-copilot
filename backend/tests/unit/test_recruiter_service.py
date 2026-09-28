"""
Unit tests for RecruiterService (Phase 10 Recruiter CRM & Networking Intelligence System).
"""
import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.recruiter_repository import RecruiterRepository
from services.recruiter_service import RecruiterService
from schemas.recruiter import (
    ContactInteractionCreateRequest,
    RecruiterCreateRequest,
    RecruiterUpdateRequest,
    ReferralCreateRequest,
    ReferralUpdateRequest,
)


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.fixture
def recruiter_service(db_session: AsyncSession) -> RecruiterService:
    repo = RecruiterRepository(session=db_session)
    return RecruiterService(recruiter_repo=repo)


@pytest.mark.asyncio
async def test_recruiter_crud_lifecycle(recruiter_service: RecruiterService, mock_user_id: uuid.UUID):
    """Test creating, updating, reading, and deleting a recruiter profile."""
    # 1. Create Recruiter
    payload = RecruiterCreateRequest(
        name="Sarah Jenkins",
        company="Stripe",
        title="Staff Technical Recruiter",
        email="sjenkins@stripe.com",
        linkedinUrl="https://linkedin.com/in/sarahjenkins-tech",
        notes="Met at Silicon Valley Tech Expo",
    )
    recruiter = await recruiter_service.createRecruiter(user_id=mock_user_id, payload=payload)
    assert recruiter.name == "Sarah Jenkins"
    assert recruiter.company == "Stripe"
    assert recruiter.title == "Staff Technical Recruiter"
    assert recruiter.email == "sjenkins@stripe.com"
    assert recruiter.interaction_count == 0
    assert recruiter.referral_count == 0

    # 2. Update Recruiter
    update_payload = RecruiterUpdateRequest(
        title="Lead Executive Recruiter",
        notes="Updated: Primary contact for Platform Engineering openings",
    )
    updated = await recruiter_service.updateRecruiter(recruiter_id=recruiter.id, payload=update_payload)
    assert updated is not None
    assert updated.title == "Lead Executive Recruiter"
    assert "Platform Engineering" in updated.notes

    # 3. Get Recruiter Detail
    detail = await recruiter_service.getRecruiter(recruiter_id=recruiter.id)
    assert detail is not None
    assert detail.name == "Sarah Jenkins"
    assert len(detail.interactions) == 0
    assert len(detail.referrals) == 0

    # 4. List Recruiters
    list_res = await recruiter_service.listRecruiters(user_id=mock_user_id, company="Stripe")
    assert list_res.total >= 1
    assert any(r.id == recruiter.id for r in list_res.recruiters)
    assert "Stripe" in list_res.companies

    # 5. Delete Recruiter
    del_ok = await recruiter_service.deleteRecruiter(recruiter_id=recruiter.id)
    assert del_ok is True
    post_del = await recruiter_service.getRecruiter(recruiter_id=recruiter.id)
    assert post_del is None


@pytest.mark.asyncio
async def test_interaction_logging_and_history(recruiter_service: RecruiterService, mock_user_id: uuid.UUID):
    """Test adding interactions and retrieving chronological contact history."""
    recruiter = await recruiter_service.createRecruiter(
        user_id=mock_user_id,
        payload=RecruiterCreateRequest(
            name="Alex Rivera",
            company="Figma",
            title="Engineering Talent Lead",
        ),
    )

    # Add Message interaction
    msg_interaction = await recruiter_service.addInteraction(
        recruiter_id=recruiter.id,
        payload=ContactInteractionCreateRequest(
            interactionType="Message",
            summary="Sent cold LinkedIn connection request and intro note.",
        ),
    )
    assert msg_interaction is not None
    assert msg_interaction.interaction_type == "Message"

    # Add Call interaction
    call_interaction = await recruiter_service.addInteraction(
        recruiter_id=recruiter.id,
        payload=ContactInteractionCreateRequest(
            interactionType="Call",
            summary="15-minute phone screening regarding Senior Full-Stack opening.",
        ),
    )
    assert call_interaction is not None
    assert call_interaction.interaction_type == "Call"

    # Fetch History
    history = await recruiter_service.getRecruiterHistory(recruiter_id=recruiter.id)
    assert len(history) == 2
    summaries = [h.summary for h in history]
    assert any("phone screening" in s for s in summaries)


@pytest.mark.asyncio
async def test_referral_pipeline_and_tracking(recruiter_service: RecruiterService, mock_user_id: uuid.UUID):
    """Test requesting a referral, updating its status, and listing referrals."""
    recruiter = await recruiter_service.createRecruiter(
        user_id=mock_user_id,
        payload=RecruiterCreateRequest(
            name="David Chen",
            company="Datadog",
            title="Senior Engineering Manager",
        ),
    )

    # 1. Add Referral (Requested)
    ref = await recruiter_service.addReferral(
        recruiter_id=recruiter.id,
        payload=ReferralCreateRequest(
            company="Datadog",
            role="Staff Infrastructure Engineer",
            status="Requested",
            notes="Submitted internal requisition link REQ-88219",
        ),
    )
    assert ref is not None
    assert ref.company == "Datadog"
    assert ref.role == "Staff Infrastructure Engineer"
    assert ref.status == "Requested"
    assert ref.recruiter_name == "David Chen"

    # Verify automatic Referral interaction was logged in history
    history = await recruiter_service.getRecruiterHistory(recruiter_id=recruiter.id)
    assert len(history) >= 1
    assert any(h.interaction_type == "Referral" for h in history)

    # 2. Update Referral to Received
    updated_ref = await recruiter_service.updateReferral(
        referral_id=ref.id,
        payload=ReferralUpdateRequest(
            status="Received",
            notes="David submitted internal portal endorsement.",
        ),
    )
    assert updated_ref is not None
    assert updated_ref.status == "Received"

    # 3. List Referrals by Status
    referrals_list = await recruiter_service.listReferrals(
        user_id=mock_user_id,
        status="Received",
    )
    assert len(referrals_list) >= 1
    assert any(r.id == ref.id for r in referrals_list)

    # 4. Delete Referral
    del_ok = await recruiter_service.deleteReferral(referral_id=ref.id)
    assert del_ok is True


@pytest.mark.asyncio
async def test_networking_analytics_calculation(recruiter_service: RecruiterService, mock_user_id: uuid.UUID):
    """Test outreach metrics, response rate, and referral success rate calculations."""
    # Create Recruiter 1: Messages sent + Call response
    r1 = await recruiter_service.createRecruiter(
        user_id=mock_user_id,
        payload=RecruiterCreateRequest(name="Elena Rostova", company="Notion"),
    )
    await recruiter_service.addInteraction(
        recruiter_id=r1.id,
        payload=ContactInteractionCreateRequest(interactionType="Message", summary="Intro outreach"),
    )
    await recruiter_service.addInteraction(
        recruiter_id=r1.id,
        payload=ContactInteractionCreateRequest(interactionType="Call", summary="Intro call completed"),
    )

    # Create Recruiter 2: Email sent + Referral
    r2 = await recruiter_service.createRecruiter(
        user_id=mock_user_id,
        payload=RecruiterCreateRequest(name="Marcus Vance", company="Linear"),
    )
    await recruiter_service.addInteraction(
        recruiter_id=r2.id,
        payload=ContactInteractionCreateRequest(interactionType="Email", summary="Portfolio follow up"),
    )
    await recruiter_service.addReferral(
        recruiter_id=r2.id,
        payload=ReferralCreateRequest(
            company="Linear",
            role="Backend Architect",
            status="Received",
        ),
    )

    analytics = await recruiter_service.getNetworkingAnalytics(user_id=mock_user_id)
    assert analytics.recruiters_contacted >= 2
    assert analytics.companies_reached >= 2
    assert analytics.messages_sent >= 2
    assert analytics.responses_received >= 1
    assert analytics.response_rate > 0.0
    assert analytics.referrals_received >= 1
    assert analytics.referral_success_rate > 0.0
    assert "Message" in analytics.interactions_by_type
    assert "Received" in analytics.referrals_by_status
