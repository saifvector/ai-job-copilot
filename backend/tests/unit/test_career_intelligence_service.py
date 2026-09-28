import uuid
from datetime import datetime, timedelta, timezone
import pytest
from models.application import ApplicationModel
from models.job import JobModel
from models.job_skill import JobSkillModel
from models.tailored_resume import TailoredResumeModel
from models.user import UserModel
from services.career_intelligence_service import CareerIntelligenceService


@pytest.mark.asyncio
async def test_career_intelligence_lifecycle_and_analytics(db_session):
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Outcome Intelligence User",
        email=f"intel_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)

    # Create 2 jobs
    job1_id = uuid.uuid4()
    job1 = JobModel(
        id=job1_id,
        source="LinkedIn",
        external_id="ext-job-1",
        title="Staff AI Engineer",
        company="Anthropic AI",
        location="Remote",
        description="LLM systems and agent orchestration",
        apply_url="https://anthropic.com/apply",
    )
    job2_id = uuid.uuid4()
    job2 = JobModel(
        id=job2_id,
        source="Referral",
        external_id="ext-job-2",
        title="Principal Backend Architect",
        company="Stripe",
        location="San Francisco, CA",
        description="High scale distributed payments engine",
        apply_url="https://stripe.com/apply",
    )
    db_session.add_all([job1, job2])

    # Add job skills
    js1 = JobSkillModel(job_id=job1_id, skill_name="Python")
    js2 = JobSkillModel(job_id=job1_id, skill_name="PyTorch")
    js3 = JobSkillModel(job_id=job2_id, skill_name="Python")
    js4 = JobSkillModel(job_id=job2_id, skill_name="Distributed Systems")
    db_session.add_all([js1, js2, js3, js4])

    # Create tailored resume
    resume_id = uuid.uuid4()
    resume = TailoredResumeModel(
        id=resume_id,
        user_id=user_id,
        job_id=job1_id,
        title="AI Engineer Tailored V1",
        summary="Specialist in AI agent architectures",
        content="{\"summary\": \"Experienced AI Architect\"}",
        ats_score=92.5,
        keyword_coverage=88.0,
    )
    db_session.add(resume)

    # Create 2 applications
    app1_id = uuid.uuid4()
    app1 = ApplicationModel(
        id=app1_id,
        user_id=user_id,
        job_id=job1_id,
        tailored_resume_id=resume_id,
        status="APPLIED",
        application_date=datetime.now(timezone.utc) - timedelta(days=5),
        source="LinkedIn",
    )
    app2_id = uuid.uuid4()
    app2 = ApplicationModel(
        id=app2_id,
        user_id=user_id,
        job_id=job2_id,
        status="APPLIED",
        application_date=datetime.now(timezone.utc) - timedelta(days=3),
        source="Referral",
    )
    db_session.add_all([app1, app2])
    await db_session.commit()

    service = CareerIntelligenceService(db_session)

    # 1. Record Outcome Event on app1: InterviewReceived
    event1 = await service.record_outcome(
        user_id=user_id,
        application_id=app1_id,
        outcome_type="InterviewReceived",
        occurred_at=datetime.now(timezone.utc) - timedelta(days=2),
        notes="Recruiter screen scheduled for Friday",
        metadata={"interview_round": 1},
    )
    assert event1.outcome_type == "InterviewReceived"
    assert event1.job_title == "Staff AI Engineer"
    assert event1.company == "Anthropic AI"

    # Verify application status was updated to INTERVIEW
    await db_session.refresh(app1)
    assert app1.status == "INTERVIEW"

    # 2. Record Outcome Event on app2: OfferReceived
    event2 = await service.record_outcome(
        user_id=user_id,
        application_id=app2_id,
        outcome_type="OfferReceived",
        occurred_at=datetime.now(timezone.utc),
        notes="Received formal written offer",
        metadata={"offer_amount": 220000},
    )
    assert event2.outcome_type == "OfferReceived"

    await db_session.refresh(app2)
    assert app2.status == "OFFER"

    # 3. Analyze Global Outcomes
    analytics = await service.analyze_outcomes(user_id)
    assert analytics.total_applications == 2
    assert analytics.interviews_received >= 1
    assert analytics.offers_received >= 1
    assert analytics.interview_rate >= 0.5
    assert analytics.offer_rate >= 0.5
    assert analytics.avg_response_days > 0.0
    assert "INTERVIEW" in analytics.active_funnel
    assert "OFFER" in analytics.active_funnel

    # 4. Calculate Resume Performance
    perf_list = await service.calculate_resume_performance(user_id)
    assert len(perf_list) >= 1
    top_resume = perf_list[0]
    assert top_resume.tailored_resume_id == resume_id
    assert top_resume.applications_sent == 1
    assert top_resume.interviews_received == 1
    assert top_resume.response_rate == 1.0

    # 5. Calculate Skill Impact
    skill_impact = await service.calculate_skill_impact(user_id)
    assert skill_impact.total >= 3
    skill_names = [s.skill_name for s in skill_impact.items]
    assert "Python" in skill_names

    # 6. Company Response Analytics
    company_analytics = await service.get_company_response_analytics(user_id)
    assert company_analytics.total_companies >= 2
    companies = [c.company for c in company_analytics.companies]
    assert "Anthropic AI" in companies
    assert "Stripe" in companies

    # 7. Application Strategy Analytics
    strategy = await service.get_application_strategy_analytics(user_id)
    assert len(strategy.source_breakdown) >= 2
    assert len(strategy.key_insights) >= 1

    # 8. Evidence-Based Recommendations
    recs = await service.get_recommendations(user_id)
    assert len(recs.recommendations) >= 2

    # 9. Historical Warehouse Snapshot
    snapshot = await service.create_snapshot(user_id)
    assert snapshot.total_applications == 2
    assert snapshot.interview_rate >= 0.5
    assert snapshot.metrics_payload is not None

    # 10. Complete Executive Overview
    overview = await service.get_overview(user_id)
    assert overview.analytics.total_applications == 2
    assert len(overview.top_resumes) >= 1
    assert len(overview.top_skills) >= 1
    assert len(overview.recommendations) >= 1
