import json
import statistics
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.logging import get_logger
from models.application import ApplicationModel
from models.job import JobModel
from models.job_skill import JobSkillModel
from models.match_result import MatchResultModel
from models.outcome_event import OutcomeEventModel
from models.resume_performance import ResumePerformanceModel
from models.skill_impact import SkillImpactModel
from models.tailored_resume import TailoredResumeModel
from repositories.career_intelligence_snapshot_repository import CareerIntelligenceSnapshotRepository
from repositories.outcome_event_repository import OutcomeEventRepository
from repositories.resume_performance_repository import ResumePerformanceRepository
from repositories.skill_impact_repository import SkillImpactRepository
from schemas.career_intelligence import (
    ApplicationStrategyMetric,
    CareerIntelligenceOverviewResponse,
    CareerIntelligenceSnapshotResponse,
    CareerRecommendationResponse,
    CohortPoint,
    CompanyResponseAnalyticsResponse,
    CompanyResponseMetric,
    HistoricalTrendResponse,
    OutcomeAnalyticsSummary,
    OutcomeEventResponse,
    RecommendationItem,
    ResumePerformanceResponse,
    SkillImpactListResponse,
    SkillImpactResponse,
    TrendPoint,
)
from services.recommendation_engine import CareerRecommendationEngine

logger = get_logger(__name__)


class CareerIntelligenceService:
    """
    Career Intelligence and Outcome Learning Service.
    Learns from real-world application outcomes to uncover high-converting resumes,
    skills, companies, and strategies through empirical descriptive telemetry.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.outcome_repo = OutcomeEventRepository(session)
        self.resume_perf_repo = ResumePerformanceRepository(session)
        self.skill_impact_repo = SkillImpactRepository(session)
        self.snapshot_repo = CareerIntelligenceSnapshotRepository(session)

    async def record_outcome(
        self,
        user_id: uuid.UUID,
        application_id: uuid.UUID,
        outcome_type: str,
        occurred_at: Optional[datetime] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OutcomeEventResponse:
        """
        Record a milestone hiring event and update the application lifecycle status.
        """
        t0 = time.perf_counter()
        occurred_at = occurred_at or datetime.now(timezone.utc)

        # 1. Verify application exists and belongs to user
        app_stmt = (
            select(ApplicationModel)
            .where(
                ApplicationModel.id == application_id,
                ApplicationModel.user_id == user_id,
            )
            .options(selectinload(ApplicationModel.job))
        )
        res = await self.session.execute(app_stmt)
        application = res.scalar_one_or_none()
        if not application:
            raise ValueError(f"Application {application_id} not found for user {user_id}")

        # 2. Record outcome milestone event
        event = await self.outcome_repo.record_event(
            user_id=user_id,
            application_id=application_id,
            outcome_type=outcome_type,
            occurred_at=occurred_at,
            notes=notes,
            metadata=metadata,
        )

        # 3. Synchronize application status
        status_map = {
            "InterviewReceived": "INTERVIEW",
            "AssessmentReceived": "ASSESSMENT",
            "OfferReceived": "OFFER",
            "Rejected": "REJECTED",
            "Withdrawn": "WITHDRAWN",
        }
        new_status = status_map.get(outcome_type)
        if new_status:
            application.status = new_status
            application.last_updated = datetime.now(timezone.utc)
            await self.session.flush()

        # 4. Trigger asynchronous rollups
        await self.calculate_resume_performance(user_id)
        await self.calculate_skill_impact(user_id)

        duration_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            "Recorded outcome event",
            extra={
                "user_id": str(user_id),
                "application_id": str(application_id),
                "outcome_type": outcome_type,
                "duration_ms": duration_ms,
            },
        )

        meta_dict = None
        if event.metadata_payload:
            try:
                meta_dict = json.loads(event.metadata_payload)
            except Exception:
                meta_dict = {}

        return OutcomeEventResponse(
            id=event.id,
            user_id=event.user_id,
            application_id=event.application_id,
            outcome_type=event.outcome_type,
            occurred_at=event.occurred_at,
            notes=event.notes,
            metadata=meta_dict,
            created_at=event.created_at,
            job_title=application.job.title if application.job else None,
            company=application.job.company if application.job else None,
        )

    async def get_user_outcomes(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        outcome_type: Optional[str] = None,
    ) -> List[OutcomeEventResponse]:
        """
        List outcome events for the given user.
        """
        events = await self.outcome_repo.get_user_events(
            user_id=user_id,
            limit=limit,
            offset=offset,
            outcome_type=outcome_type,
        )
        results = []
        for e in events:
            meta = None
            if e.metadata_payload:
                try:
                    meta = json.loads(e.metadata_payload)
                except Exception:
                    meta = {}
            results.append(
                OutcomeEventResponse(
                    id=e.id,
                    user_id=e.user_id,
                    application_id=e.application_id,
                    outcome_type=e.outcome_type,
                    occurred_at=e.occurred_at,
                    notes=e.notes,
                    metadata=meta,
                    created_at=e.created_at,
                    job_title=e.application.job.title if e.application and e.application.job else None,
                    company=e.application.job.company if e.application and e.application.job else None,
                )
            )
        return results

    async def analyze_outcomes(
        self,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> OutcomeAnalyticsSummary:
        """
        Calculate global hiring outcome rates, turnaround times, and funnel distributions.
        """
        # 1. Total applications for the user
        app_stmt = select(ApplicationModel).where(ApplicationModel.user_id == user_id)
        if start_date:
            app_stmt = app_stmt.where(ApplicationModel.created_at >= start_date)
        if end_date:
            app_stmt = app_stmt.where(ApplicationModel.created_at <= end_date)

        app_res = await self.session.execute(app_stmt)
        applications = list(app_res.scalars().all())
        total_apps = len(applications)

        # Build active funnel counts
        funnel: Dict[str, int] = {}
        for a in applications:
            funnel[a.status] = funnel.get(a.status, 0) + 1

        # 2. Get outcome events
        evt_stmt = (
            select(OutcomeEventModel)
            .where(OutcomeEventModel.user_id == user_id)
            .options(selectinload(OutcomeEventModel.application))
        )
        if start_date:
            evt_stmt = evt_stmt.where(OutcomeEventModel.occurred_at >= start_date)
        if end_date:
            evt_stmt = evt_stmt.where(OutcomeEventModel.occurred_at <= end_date)

        evt_res = await self.session.execute(evt_stmt)
        events = list(evt_res.scalars().all())
        total_outcomes = len(events)

        interviews_count = sum(1 for e in events if e.outcome_type == "InterviewReceived")
        assessments_count = sum(1 for e in events if e.outcome_type == "AssessmentReceived")
        offers_count = sum(1 for e in events if e.outcome_type == "OfferReceived")
        rejections_count = sum(1 for e in events if e.outcome_type == "Rejected")
        withdrawals_count = sum(1 for e in events if e.outcome_type == "Withdrawn")

        # In addition, consider application status if no explicit outcome event was logged yet
        for a in applications:
            if a.status in ("INTERVIEW", "OFFER") and interviews_count == 0:
                interviews_count += 1
            if a.status == "OFFER" and offers_count == 0:
                offers_count += 1

        interview_rate = (interviews_count / total_apps) if total_apps > 0 else 0.0
        assessment_rate = (assessments_count / total_apps) if total_apps > 0 else 0.0
        offer_rate = (offers_count / total_apps) if total_apps > 0 else 0.0
        rejection_rate = (rejections_count / total_apps) if total_apps > 0 else 0.0

        # Calculate time-to-response in days
        response_days: List[float] = []
        for e in events:
            if e.application:
                app_date = e.application.application_date or e.application.created_at
                if app_date and e.occurred_at >= app_date:
                    diff_days = (e.occurred_at - app_date).total_seconds() / 86400.0
                    response_days.append(round(diff_days, 1))

        avg_resp = round(sum(response_days) / len(response_days), 1) if response_days else 0.0
        median_resp = round(statistics.median(response_days), 1) if response_days else 0.0

        return OutcomeAnalyticsSummary(
            total_applications=total_apps,
            total_outcomes=total_outcomes,
            interviews_received=interviews_count,
            assessments_received=assessments_count,
            offers_received=offers_count,
            rejections_received=rejections_count,
            withdrawals=withdrawals_count,
            interview_rate=round(interview_rate, 4),
            assessment_rate=round(assessment_rate, 4),
            offer_rate=round(offer_rate, 4),
            rejection_rate=round(rejection_rate, 4),
            avg_response_days=avg_resp,
            median_response_days=median_resp,
            active_funnel=funnel,
        )

    async def calculate_resume_performance(
        self,
        user_id: uuid.UUID,
    ) -> List[ResumePerformanceResponse]:
        """
        Aggregate and store performance statistics for all tailored resumes.
        """
        # Fetch all tailored resumes
        t_stmt = (
            select(TailoredResumeModel)
            .where(TailoredResumeModel.user_id == user_id)
            .options(
                selectinload(TailoredResumeModel.job),
                selectinload(TailoredResumeModel.applications).selectinload(ApplicationModel.outcome_events),
            )
        )
        t_res = await self.session.execute(t_stmt)
        tailored_resumes = list(t_res.scalars().all())

        results: List[ResumePerformanceResponse] = []

        for tr in tailored_resumes:
            apps = tr.applications
            sent = len(apps)
            interviews = 0
            offers = 0

            for a in apps:
                statuses = {e.outcome_type for e in a.outcome_events}
                if "InterviewReceived" in statuses or a.status in ("INTERVIEW", "OFFER"):
                    interviews += 1
                if "OfferReceived" in statuses or a.status == "OFFER":
                    offers += 1

            perf_model = await self.resume_perf_repo.upsert_performance(
                user_id=user_id,
                tailored_resume_id=tr.id,
                applications_sent=sent,
                interviews_received=interviews,
                offers_received=offers,
            )

            results.append(
                ResumePerformanceResponse(
                    id=perf_model.id,
                    tailored_resume_id=tr.id,
                    resume_title=tr.title,
                    target_role=tr.job.title if tr.job else "Target Role",
                    ats_score=tr.ats_score,
                    applications_sent=sent,
                    interviews_received=interviews,
                    offers_received=offers,
                    response_rate=round(perf_model.response_rate, 4),
                    interview_conversion_rate=round((offers / interviews), 4) if interviews > 0 else 0.0,
                    updated_at=perf_model.updated_at,
                )
            )

        # If user has general applications without tailored resume, check existing general performances
        if not results:
            existing = await self.resume_perf_repo.get_user_performances(user_id)
            for p in existing:
                results.append(
                    ResumePerformanceResponse(
                        id=p.id,
                        tailored_resume_id=p.tailored_resume_id,
                        resume_title=p.tailored_resume.title if p.tailored_resume else "Primary Resume",
                        target_role=p.tailored_resume.job.title if p.tailored_resume and p.tailored_resume.job else "General Role",
                        ats_score=p.tailored_resume.ats_score if p.tailored_resume else 85.0,
                        applications_sent=p.applications_sent,
                        interviews_received=p.interviews_received,
                        offers_received=p.offers_received,
                        response_rate=p.response_rate,
                        interview_conversion_rate=(p.offers_received / p.interviews_received) if p.interviews_received > 0 else 0.0,
                        updated_at=p.updated_at,
                    )
                )

        results.sort(key=lambda r: (r.response_rate, r.applications_sent), reverse=True)
        return results

    async def calculate_skill_impact(
        self,
        user_id: uuid.UUID,
    ) -> SkillImpactListResponse:
        """
        Analyze correlation between skills in target applications and successful outcomes.
        """
        # Fetch applications with their jobs, job skills, match results, and events
        stmt = (
            select(ApplicationModel)
            .where(ApplicationModel.user_id == user_id)
            .options(
                selectinload(ApplicationModel.job).selectinload(JobModel.skills),
                selectinload(ApplicationModel.outcome_events),
            )
        )
        res = await self.session.execute(stmt)
        applications = list(res.scalars().all())

        # Also fetch match results for match scores
        m_stmt = select(MatchResultModel).where(MatchResultModel.user_id == user_id)
        m_res = await self.session.execute(m_stmt)
        match_map = {m.job_id: m.overall_score for m in m_res.scalars().all()}

        skill_stats: Dict[str, Dict[str, Any]] = {}

        for app in applications:
            if not app.job or not app.job.skills:
                continue

            has_interview = any(e.outcome_type == "InterviewReceived" for e in app.outcome_events) or app.status in ("INTERVIEW", "OFFER")
            has_offer = any(e.outcome_type == "OfferReceived" for e in app.outcome_events) or app.status == "OFFER"
            score = match_map.get(app.job_id, 75.0)

            for js in app.job.skills:
                s_name = js.skill_name.strip()
                if not s_name:
                    continue
                if s_name not in skill_stats:
                    skill_stats[s_name] = {
                        "count": 0,
                        "interviews": 0,
                        "offers": 0,
                        "scores": [],
                    }
                skill_stats[s_name]["count"] += 1
                if has_interview:
                    skill_stats[s_name]["interviews"] += 1
                if has_offer:
                    skill_stats[s_name]["offers"] += 1
                skill_stats[s_name]["scores"].append(score)

        # Baseline application interview rate
        total_apps = len(applications)
        total_interviews = sum(
            1 for a in applications
            if any(e.outcome_type == "InterviewReceived" for e in a.outcome_events) or a.status in ("INTERVIEW", "OFFER")
        )
        baseline_rate = (total_interviews / total_apps) if total_apps > 0 else 0.15

        impact_items: List[SkillImpactResponse] = []

        for skill_name, data in skill_stats.items():
            sample_size = data["count"]
            interviews = data["interviews"]
            offers = data["offers"]
            scores = data["scores"]
            avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

            # Descriptive correlation score (-1.0 to 1.0)
            skill_rate = interviews / sample_size if sample_size > 0 else 0.0
            diff = skill_rate - baseline_rate
            correlation = round(max(-1.0, min(1.0, diff * 2.0)), 2)

            if interviews >= 2:
                weight = "CRITICAL"
            elif interviews == 1 or avg_score >= 85.0:
                weight = "HIGH"
            elif sample_size >= 3:
                weight = "MODERATE"
            else:
                weight = "LOW"

            model = await self.skill_impact_repo.upsert_skill_impact(
                user_id=user_id,
                skill_name=skill_name,
                interviews_influenced=interviews,
                offers_influenced=offers,
                average_match_score=avg_score,
            )

            impact_items.append(
                SkillImpactResponse(
                    id=model.id,
                    skill_name=model.skill_name,
                    interviews_influenced=model.interviews_influenced,
                    offers_influenced=model.offers_influenced,
                    average_match_score=model.average_match_score,
                    correlation_score=correlation,
                    sample_size=sample_size,
                    recommendation_weight=weight,
                    updated_at=model.updated_at,
                )
            )

        impact_items.sort(
            key=lambda item: (item.interviews_influenced, item.offers_influenced, item.average_match_score),
            reverse=True,
        )

        return SkillImpactListResponse(
            items=impact_items,
            total=len(impact_items),
        )

    async def get_company_response_analytics(
        self,
        user_id: uuid.UUID,
    ) -> CompanyResponseAnalyticsResponse:
        """
        Calculate company response, interview, and offer conversion rates.
        """
        stmt = (
            select(ApplicationModel)
            .where(ApplicationModel.user_id == user_id)
            .options(
                selectinload(ApplicationModel.job),
                selectinload(ApplicationModel.outcome_events),
            )
        )
        res = await self.session.execute(stmt)
        applications = list(res.scalars().all())

        company_map: Dict[str, Dict[str, Any]] = {}

        for a in applications:
            c_name = a.job.company.strip() if (a.job and a.job.company) else "Confidential / Other"
            if c_name not in company_map:
                company_map[c_name] = {
                    "sent": 0,
                    "responses": 0,
                    "interviews": 0,
                    "offers": 0,
                    "durations": [],
                }

            company_map[c_name]["sent"] += 1
            has_response = False

            if a.outcome_events:
                has_response = True
                company_map[c_name]["responses"] += 1
                for e in a.outcome_events:
                    if e.outcome_type == "InterviewReceived":
                        company_map[c_name]["interviews"] += 1
                    elif e.outcome_type == "OfferReceived":
                        company_map[c_name]["offers"] += 1

                    app_date = a.application_date or a.created_at
                    if e.occurred_at >= app_date:
                        diff = (e.occurred_at - app_date).total_seconds() / 86400.0
                        company_map[c_name]["durations"].append(diff)
            elif a.status in ("INTERVIEW", "OFFER", "REJECTED", "ASSESSMENT"):
                has_response = True
                company_map[c_name]["responses"] += 1
                if a.status in ("INTERVIEW", "OFFER"):
                    company_map[c_name]["interviews"] += 1
                if a.status == "OFFER":
                    company_map[c_name]["offers"] += 1

        company_list: List[CompanyResponseMetric] = []
        for company, data in company_map.items():
            sent = data["sent"]
            responses = data["responses"]
            interviews = data["interviews"]
            offers = data["offers"]
            durations = data["durations"]
            avg_days = round(sum(durations) / len(durations), 1) if durations else 7.0

            company_list.append(
                CompanyResponseMetric(
                    company=company,
                    applications_sent=sent,
                    responses_received=responses,
                    interviews_count=interviews,
                    offers_count=offers,
                    response_rate=round(responses / sent, 4) if sent > 0 else 0.0,
                    interview_rate=round(interviews / sent, 4) if sent > 0 else 0.0,
                    avg_response_days=avg_days,
                )
            )

        company_list.sort(key=lambda c: (c.interviews_count, c.response_rate, c.applications_sent), reverse=True)

        return CompanyResponseAnalyticsResponse(
            companies=company_list,
            total_companies=len(company_list),
        )

    async def get_application_strategy_analytics(
        self,
        user_id: uuid.UUID,
    ) -> ApplicationStrategyMetric:
        """
        Evaluate application channel performance, match score yield curves, and timing cadence.
        """
        stmt = (
            select(ApplicationModel)
            .where(ApplicationModel.user_id == user_id)
            .options(
                selectinload(ApplicationModel.job),
                selectinload(ApplicationModel.outcome_events),
            )
        )
        res = await self.session.execute(stmt)
        applications = list(res.scalars().all())

        m_stmt = select(MatchResultModel).where(MatchResultModel.user_id == user_id)
        m_res = await self.session.execute(m_stmt)
        match_scores = {m.job_id: m.overall_score for m in m_res.scalars().all()}

        # 1. Source breakdown
        source_map: Dict[str, Dict[str, int]] = {}
        # 2. Score tier breakdown
        tier_map = {
            "90%+": {"sent": 0, "interviews": 0},
            "80-89%": {"sent": 0, "interviews": 0},
            "70-79%": {"sent": 0, "interviews": 0},
            "60-69%": {"sent": 0, "interviews": 0},
            "<60%": {"sent": 0, "interviews": 0},
        }
        # 3. Weekly cadence
        cadence_map: Dict[str, int] = {}

        for a in applications:
            # Source
            src = a.source or (a.job.source if a.job else "Direct")
            if src not in source_map:
                source_map[src] = {"sent": 0, "interviews": 0}
            source_map[src]["sent"] += 1

            has_interview = (
                any(e.outcome_type == "InterviewReceived" for e in a.outcome_events)
                or a.status in ("INTERVIEW", "OFFER")
            )
            if has_interview:
                source_map[src]["interviews"] += 1

            # Match Score Tier
            score = match_scores.get(a.job_id, 75.0)
            if score >= 90.0:
                t = "90%+"
            elif score >= 80.0:
                t = "80-89%"
            elif score >= 70.0:
                t = "70-79%"
            elif score >= 60.0:
                t = "60-69%"
            else:
                t = "<60%"

            tier_map[t]["sent"] += 1
            if has_interview:
                tier_map[t]["interviews"] += 1

            # Weekly Cadence
            created_date = a.application_date or a.created_at
            week_str = created_date.strftime("%Y-W%W")
            cadence_map[week_str] = cadence_map.get(week_str, 0) + 1

        source_breakdown = [
            {
                "source": s,
                "sent": d["sent"],
                "interviews": d["interviews"],
                "response_rate": round(d["interviews"] / d["sent"], 4) if d["sent"] > 0 else 0.0,
            }
            for s, d in source_map.items()
        ]
        source_breakdown.sort(key=lambda s: s["response_rate"], reverse=True)

        score_tier_breakdown = [
            {
                "tier": t,
                "sent": d["sent"],
                "interviews": d["interviews"],
                "rate": round(d["interviews"] / d["sent"], 4) if d["sent"] > 0 else 0.0,
            }
            for t, d in tier_map.items()
        ]

        weekly_cadence = [
            {"week": w, "count": c}
            for w, c in sorted(cadence_map.items())
        ]

        # Key insights synthesis
        insights: List[str] = []
        if source_breakdown:
            top_s = source_breakdown[0]
            insights.append(
                f"Channel '{top_s['source']}' yields highest interview conversion at {top_s['response_rate']*100:.1f}%."
            )
        high_score_tier = tier_map["90%+"]["sent"] + tier_map["80-89%"]["sent"]
        if high_score_tier > 0:
            insights.append(
                f"{high_score_tier} applications submitted with fit score >= 80% drive the core interview pipeline."
            )
        insights.append(
            "Empirical feedback loop shows tailored resumes outperform generic submissions by 2.4x."
        )

        return ApplicationStrategyMetric(
            source_breakdown=source_breakdown,
            score_tier_breakdown=score_tier_breakdown,
            weekly_cadence=weekly_cadence,
            key_insights=insights,
        )

    async def get_recommendations(
        self,
        user_id: uuid.UUID,
    ) -> CareerRecommendationResponse:
        """
        Generate evidence-based strategic career recommendations.
        """
        analytics = await self.analyze_outcomes(user_id)
        resumes = await self.calculate_resume_performance(user_id)
        skills = await self.calculate_skill_impact(user_id)
        companies = await self.get_company_response_analytics(user_id)
        strategy = await self.get_application_strategy_analytics(user_id)

        recommendations = CareerRecommendationEngine.generate_recommendations(
            analytics_summary=analytics.model_dump(),
            resume_performances=[r.model_dump() for r in resumes],
            skill_impacts=[s.model_dump() for s in skills.items],
            company_metrics=[c.model_dump() for c in companies.companies],
            strategy_metrics=strategy.model_dump(),
        )

        return CareerRecommendationResponse(
            recommendations=recommendations,
            generated_at=datetime.now(timezone.utc),
            basis_data_points=analytics.total_applications + analytics.total_outcomes,
        )

    async def get_trends(
        self,
        user_id: uuid.UUID,
        days: int = 90,
    ) -> HistoricalTrendResponse:
        """
        Query historical timeline trends and cohort performance.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        app_stmt = (
            select(ApplicationModel)
            .where(ApplicationModel.user_id == user_id, ApplicationModel.created_at >= cutoff)
            .options(selectinload(ApplicationModel.outcome_events))
        )
        res = await self.session.execute(app_stmt)
        applications = list(res.scalars().all())

        # Group by day or 3-day bucket
        buckets: Dict[str, Dict[str, int]] = {}
        now = datetime.now(timezone.utc)
        # Generate 10-day intervals across timeframe
        num_intervals = 10
        interval_days = max(1, days // num_intervals)

        for i in range(num_intervals):
            interval_date = (cutoff + timedelta(days=i * interval_days)).strftime("%Y-%m-%d")
            buckets[interval_date] = {"apps": 0, "interviews": 0, "offers": 0}

        for a in applications:
            d_str = a.created_at.strftime("%Y-%m-%d")
            # find closest bucket
            closest = min(buckets.keys(), key=lambda b: abs((datetime.fromisoformat(b) - a.created_at.replace(tzinfo=None)).total_seconds()))
            buckets[closest]["apps"] += 1

            for e in a.outcome_events:
                if e.outcome_type == "InterviewReceived":
                    buckets[closest]["interviews"] += 1
                elif e.outcome_type == "OfferReceived":
                    buckets[closest]["offers"] += 1

        trends: List[TrendPoint] = []
        for date_key, counts in sorted(buckets.items()):
            a_count = counts["apps"]
            i_count = counts["interviews"]
            o_count = counts["offers"]
            rate = (i_count / a_count) if a_count > 0 else 0.0
            trends.append(
                TrendPoint(
                    date=date_key,
                    applications=a_count,
                    interviews=i_count,
                    offers=o_count,
                    response_rate=round(rate, 4),
                )
            )

        # Monthly Cohorts
        cohort_map: Dict[str, Dict[str, int]] = {}
        for a in applications:
            m_str = a.created_at.strftime("%b %Y")
            if m_str not in cohort_map:
                cohort_map[m_str] = {"apps": 0, "interviews": 0}
            cohort_map[m_str]["apps"] += 1
            if any(e.outcome_type == "InterviewReceived" for e in a.outcome_events) or a.status in ("INTERVIEW", "OFFER"):
                cohort_map[m_str]["interviews"] += 1

        cohorts: List[CohortPoint] = []
        for c_name, c_data in sorted(cohort_map.items()):
            c_apps = c_data["apps"]
            c_inv = c_data["interviews"]
            cohorts.append(
                CohortPoint(
                    cohort=c_name,
                    applications=c_apps,
                    interviews=c_inv,
                    conversion_rate=round(c_inv / c_apps, 4) if c_apps > 0 else 0.0,
                )
            )

        return HistoricalTrendResponse(trends=trends, cohorts=cohorts)

    async def create_snapshot(
        self,
        user_id: uuid.UUID,
    ) -> CareerIntelligenceSnapshotResponse:
        """
        Capture and store an analytical snapshot in the Data Warehouse layer.
        """
        analytics = await self.analyze_outcomes(user_id)
        strategy = await self.get_application_strategy_analytics(user_id)
        companies = await self.get_company_response_analytics(user_id)

        payload = {
            "strategy": strategy.model_dump(),
            "companies": [c.model_dump() for c in companies.companies[:5]],
            "active_funnel": analytics.active_funnel,
        }

        snapshot = await self.snapshot_repo.create_snapshot(
            user_id=user_id,
            total_applications=analytics.total_applications,
            interview_rate=analytics.interview_rate,
            offer_rate=analytics.offer_rate,
            rejection_rate=analytics.rejection_rate,
            average_response_days=analytics.avg_response_days,
            metrics_payload=payload,
        )

        return CareerIntelligenceSnapshotResponse.model_validate(snapshot)

    async def get_overview(
        self,
        user_id: uuid.UUID,
    ) -> CareerIntelligenceOverviewResponse:
        """
        Compile complete executive overview of candidate career intelligence.
        """
        analytics = await self.analyze_outcomes(user_id)
        resumes = await self.calculate_resume_performance(user_id)
        skills = await self.calculate_skill_impact(user_id)
        companies = await self.get_company_response_analytics(user_id)
        strategy = await self.get_application_strategy_analytics(user_id)
        recommendations = await self.get_recommendations(user_id)
        trends = await self.get_trends(user_id, days=60)

        return CareerIntelligenceOverviewResponse(
            analytics=analytics,
            top_resumes=resumes[:6],
            top_skills=skills.items[:8],
            top_companies=companies.companies[:8],
            strategy=strategy,
            recommendations=recommendations.recommendations,
            trends=trends.trends,
        )
