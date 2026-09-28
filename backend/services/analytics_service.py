"""
AnalyticsService for Phase 6 Dashboard and Analytics Workspace.
Implements algorithms for:
- Dashboard Overview aggregation & KPI generation
- Profile Health calculation (Resume, Skills, Experience, Education)
- Career Readiness scoring & diagnosis
- Skill Gap Analysis (Most requested, Missing, Emerging, Recommendations)
- Analytics Snapshots & Historical trend tracking
- Performance caching and latency tracking
"""
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from models.analytics_snapshot import AnalyticsSnapshotModel
from models.match_result import MatchResultModel
from repositories.analytics_repository import AnalyticsRepository
from repositories.candidate_intelligence_repository import (
    EducationRepository,
    ExperienceRepository,
    SkillRepository,
)
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from repositories.user_repository import UserRepository
from schemas.analytics import (
    AnalyticsDashboardResponse,
    AnalyticsSnapshotItem,
    CareerReadinessFactors,
    CareerReadinessResponse,
    DashboardOverviewResponse,
    DashboardTrends,
    DistributionItem,
    LocationDistributionItem,
    MatchDistributionData,
    MatchInsightItem,
    MissingSkillItem,
    ProfileHealthBreakdown,
    ProfileHealthResponse,
    SkillFrequencyItem,
    SkillGapAnalysisResponse,
    TopSkillDemandItem,
)


class AnalyticsService:
    """
    Core business logic and analytics computation engine for AI Job Copilot.
    """

    def __init__(
        self,
        analytics_repo: AnalyticsRepository,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
        resume_repo: ResumeRepository,
        skill_repo: SkillRepository,
        experience_repo: ExperienceRepository,
        education_repo: EducationRepository,
    ) -> None:
        self.analytics_repo = analytics_repo
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.resume_repo = resume_repo
        self.skill_repo = skill_repo
        self.experience_repo = experience_repo
        self.education_repo = education_repo
        # In-memory short-term cache for rapid dashboard refreshes (key: (user_id, metric), value: (timestamp, data))
        self._cache: Dict[Tuple[str, str], Tuple[float, Any]] = {}
        self._cache_ttl_seconds = 15.0

    def _get_cached(self, user_id: str, key: str) -> Optional[Any]:
        cache_key = (user_id, key)
        if cache_key in self._cache:
            ts, val = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl_seconds:
                return val
            del self._cache[cache_key]
        return None

    def _set_cached(self, user_id: str, key: str, val: Any) -> None:
        self._cache[(user_id, key)] = (time.time(), val)

    def invalidate_user_cache(self, user_id: Union[uuid.UUID, str]) -> None:
        """Clear cache entries for a given user on updates."""
        uid_str = str(user_id)
        keys_to_del = [k for k in self._cache if k[0] == uid_str]
        for k in keys_to_del:
            self._cache.pop(k, None)

    async def calculateProfileHealth(
        self, user_id: Union[uuid.UUID, str]
    ) -> ProfileHealthResponse:
        """
        Calculate Profile Health Score (0 - 100%) across 4 core pillars (25% each):
        1. Resume Completeness
        2. Skill Coverage
        3. Experience Coverage
        4. Education Coverage
        """
        uid = uuid.UUID(str(user_id))
        uid_str = str(uid)
        cached = self._get_cached(uid_str, "profile_health")
        if cached:
            return cached

        # Fetch candidate entities in parallel / sequence
        profile = await self.profile_repo.get_by_user_id(uid)
        resume = await self.resume_repo.find_by_user(uid)
        skills = await self.skill_repo.get_by_user_id(uid)
        experiences = await self.experience_repo.get_by_user_id(uid)
        educations = await self.education_repo.get_by_user_id(uid)

        # 1. Resume Completeness (0-100)
        resume_score = 0.0
        if resume:
            resume_score += 40.0  # Resume file is uploaded
        if profile and profile.summary and len(profile.summary.strip()) > 30:
            resume_score += 30.0  # Quality summary statement
        if profile and profile.preferred_roles and len(profile.preferred_roles) > 0:
            resume_score += 15.0  # Defined role focus
        if profile and profile.years_of_experience and profile.years_of_experience > 0:
            resume_score += 15.0  # Seniority quantified
        resume_score = min(100.0, resume_score)

        # 2. Skill Coverage (0-100)
        skill_count = len(skills)
        if skill_count >= 10:
            skill_score = 100.0
        elif skill_count >= 7:
            skill_score = 85.0
        elif skill_count >= 4:
            skill_score = 70.0
        elif skill_count >= 1:
            skill_score = 50.0
        else:
            skill_score = 15.0

        # Category diversity bonus
        categories: Set[str] = {s.category for s in skills if s.category}
        if len(categories) >= 3 and skill_score < 100.0:
            skill_score = min(100.0, skill_score + 10.0)

        # 3. Experience Coverage (0-100)
        exp_count = len(experiences)
        if exp_count >= 3:
            exp_score = 100.0
        elif exp_count == 2:
            exp_score = 85.0
        elif exp_count == 1:
            exp_score = 65.0
        else:
            # Fallback if profile specifies years > 0
            if profile and profile.years_of_experience > 0:
                exp_score = 40.0
            else:
                exp_score = 15.0

        # 4. Education Coverage (0-100)
        edu_count = len(educations)
        if edu_count >= 1:
            has_degree = any(e.degree for e in educations)
            has_field = any(e.field_of_study for e in educations)
            if has_degree and has_field:
                edu_score = 100.0
            elif has_degree:
                edu_score = 80.0
            else:
                edu_score = 65.0
        else:
            edu_score = 25.0

        # Weighted calculation
        overall = round(
            0.25 * resume_score
            + 0.25 * skill_score
            + 0.25 * exp_score
            + 0.25 * edu_score,
            1,
        )

        strengths: List[str] = []
        if resume:
            strengths.append(f"Resume document uploaded ({resume.original_filename})")
        if skill_count >= 5:
            strengths.append(f"Strong skill repository with {skill_count} verified competencies")
        if exp_count >= 1:
            strengths.append(f"{exp_count} detailed employment position(s) recorded")
        if edu_count >= 1:
            strengths.append("Academic background validated")

        recommendations: List[str] = []
        if not resume:
            recommendations.append("Upload your latest PDF/DOCX resume to unlock AI profile tailoring.")
        if skill_count < 8:
            recommendations.append(f"Add at least {max(1, 8 - skill_count)} more technical or domain skills.")
        if exp_count == 0:
            recommendations.append("Add your recent employment roles with responsibilities and impact metrics.")
        if edu_count == 0:
            recommendations.append("Add your degree or training certifications to boost recruiter visibility.")
        if profile and (not profile.summary or len(profile.summary.strip()) < 30):
            recommendations.append("Enhance your candidate summary with target seniority and leadership scope.")

        response = ProfileHealthResponse(
            overall_score=overall,
            breakdown=ProfileHealthBreakdown(
                resume_completeness=round(resume_score, 1),
                skill_coverage=round(skill_score, 1),
                experience_coverage=round(exp_score, 1),
                education_coverage=round(edu_score, 1),
            ),
            strengths=strengths,
            actionable_recommendations=recommendations,
            last_updated=datetime.now(timezone.utc),
        )
        self._set_cached(uid_str, "profile_health", response)
        return response

    async def calculateCareerReadiness(
        self, user_id: Union[uuid.UUID, str]
    ) -> CareerReadinessResponse:
        """
        Calculate Career Readiness Score (0-100%) based on:
        - Resume Quality (25%)
        - Skills Alignment (30%)
        - Experience Depth (25%)
        - Market Match Rate (20%)
        """
        uid = uuid.UUID(str(user_id))
        uid_str = str(uid)
        cached = self._get_cached(uid_str, "career_readiness")
        if cached:
            return cached

        health = await self.calculateProfileHealth(uid)
        match_stats = await self.analytics_repo.get_match_distribution(uid)

        # 1. Resume Quality (from health breakdown)
        resume_quality = health.breakdown.resume_completeness

        # 2. Skills Alignment (from health + match counts)
        total_matches = match_stats["total"]
        if total_matches > 0:
            high_fit_ratio = (match_stats["excellent"] + match_stats["strong"]) / total_matches
            skills_alignment = round(
                (health.breakdown.skill_coverage * 0.5) + (high_fit_ratio * 100.0 * 0.5), 1
            )
        else:
            skills_alignment = health.breakdown.skill_coverage

        # 3. Experience Depth (from experience coverage & profile years)
        exp_depth = health.breakdown.experience_coverage

        # 4. Market Match Rate (% of matches >= 70%)
        if total_matches > 0:
            market_rate = round(
                ((match_stats["excellent"] + match_stats["strong"]) / total_matches) * 100.0, 1
            )
        else:
            market_rate = 50.0  # Baseline expectation when discovery is pending

        # Blended Readiness
        readiness_score = round(
            0.25 * resume_quality
            + 0.30 * skills_alignment
            + 0.25 * exp_depth
            + 0.20 * market_rate,
            1,
        )

        if readiness_score >= 85.0:
            tier = "Market Leader"
            explanation = (
                "Your profile exhibits exceptional readiness. Your competencies align closely "
                "with top-tier compensation brackets and employers actively seeking your stack."
            )
        elif readiness_score >= 70.0:
            tier = "Market Ready"
            explanation = (
                "You possess strong competitive positioning across current job postings. "
                "Addressing a few high-demand missing skills will unlock top-percentile matches."
            )
        elif readiness_score >= 55.0:
            tier = "Advancing Competency"
            explanation = (
                "Solid foundation established. Focus on highlighting measurable project results "
                "and filling cloud/infrastructure requirements to reach the top tier."
            )
        else:
            tier = "Developing Profile"
            explanation = (
                "Profile requires foundational updates. Upload a comprehensive resume and "
                "populate your verified technical competencies to generate high-fit job matches."
            )

        # Gather key competencies
        candidate_skills = await self.skill_repo.get_by_user_id(uid)
        competencies = [str(s.name) for s in sorted(candidate_skills, key=lambda x: getattr(x, 'confidence_score', 0.8), reverse=True)[:5]]

        growth_priorities = [
            "Align profile keywords with emerging tech stacks.",
            "Complete portfolio projects showcasing end-to-end delivery.",
            "Target high-frequency missing skills identified in matched jobs.",
        ]

        response = CareerReadinessResponse(
            career_readiness_score=readiness_score,
            tier=tier,
            factors=CareerReadinessFactors(
                resume_quality=round(resume_quality, 1),
                skills_alignment=round(skills_alignment, 1),
                experience_depth=round(exp_depth, 1),
                market_match_rate=round(market_rate, 1),
            ),
            explanation=explanation,
            key_competencies=competencies,
            growth_priorities=growth_priorities,
            generated_at=datetime.now(timezone.utc),
        )
        self._set_cached(uid_str, "career_readiness", response)
        return response

    async def generateSkillGapAnalysis(
        self, user_id: Union[uuid.UUID, str]
    ) -> SkillGapAnalysisResponse:
        """
        Analyze all matched opportunities to extract:
        - Most Requested Skills
        - Missing Skills (skills demanded that the user lacks)
        - Emerging Skills (modern high-growth competencies)
        - Actionable learning recommendations
        """
        uid = uuid.UUID(str(user_id))
        uid_str = str(uid)
        cached = self._get_cached(uid_str, "skill_gap_analysis")
        if cached:
            return cached

        matches = await self.analytics_repo.get_all_matches_with_jobs(uid, limit=200)
        candidate_skills = await self.skill_repo.get_by_user_id(uid)
        candidate_skill_names_lower = {s.name.strip().lower(): s.name for s in candidate_skills}

        # Skill frequency tallies
        job_skill_counts: Dict[str, int] = {}
        missing_skill_counts: Dict[str, int] = {}

        total_analyzed = len(matches)

        for m in matches:
            # Missing skills recorded during matching
            if m.missing_skills:
                for ms in m.missing_skills:
                    clean = ms.strip()
                    if clean:
                        missing_skill_counts[clean] = missing_skill_counts.get(clean, 0) + 1

            # Job skill tags
            if m.job and m.job.skills:
                for js in m.job.skills:
                    sname = js.skill_name.strip()
                    if sname:
                        job_skill_counts[sname] = job_skill_counts.get(sname, 0) + 1

        # If job_skills table was sparse, backfill from missing_skills + candidate skills
        if not job_skill_counts and missing_skill_counts:
            for ms, count in missing_skill_counts.items():
                job_skill_counts[ms] = count
            for cs in candidate_skills:
                job_skill_counts[cs.name] = max(1, int(total_analyzed * 0.6))

        # Default fallback sample skills if no matches have occurred yet
        if not job_skill_counts:
            default_samples = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "TypeScript", "React", "GraphQL"]
            for s in default_samples:
                job_skill_counts[s] = 1

        denom = max(1, total_analyzed)

        # Build Most Requested Skills
        most_requested: List[SkillFrequencyItem] = []
        for sname, count in sorted(job_skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            has_it = sname.lower() in candidate_skill_names_lower
            pct = round((count / denom) * 100.0, 1)
            most_requested.append(
                SkillFrequencyItem(
                    name=sname,
                    count=count,
                    percentage=pct,
                    in_candidate_profile=has_it,
                    category="Core Technology",
                )
            )

        # Build Missing Skills
        missing_items: List[SkillFrequencyItem] = []
        for sname, count in sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)[:12]:
            pct = round((count / denom) * 100.0, 1)
            priority = "High" if pct >= 25.0 else ("Medium" if pct >= 10.0 else "Low")
            missing_items.append(
                SkillFrequencyItem(
                    name=sname,
                    count=count,
                    percentage=pct,
                    in_candidate_profile=False,
                    priority=priority,
                    recommendation=f"Featured in {count} matched roles. Adding proficiency will elevate match scores.",
                )
            )

        # Emerging skills (modern stack keywords)
        emerging_keywords = {"Kubernetes", "AWS", "GCP", "GraphQL", "Tailwind", "Next.js", "AI/ML", "LangChain", "FastAPI", "Kafka", "Rust"}
        emerging_items: List[SkillFrequencyItem] = []
        for sname, count in job_skill_counts.items():
            if sname in emerging_keywords or any(k.lower() in sname.lower() for k in emerging_keywords):
                has_it = sname.lower() in candidate_skill_names_lower
                emerging_items.append(
                    SkillFrequencyItem(
                        name=sname,
                        count=count,
                        percentage=round((count / denom) * 100.0, 1),
                        in_candidate_profile=has_it,
                        category="High-Growth",
                    )
                )
        emerging_items.sort(key=lambda x: x.count, reverse=True)

        # Recommendations
        recommendations = [
            f"Prioritize acquiring top missing skills: {', '.join([m.name for m in missing_items[:3]]) or 'Cloud deployment (AWS/Docker)'}."
            if missing_items
            else "Maintain your well-rounded skill coverage across modern fullstack tools.",
            "Include technical project descriptions demonstrating your real-world usage of these competencies.",
            "Re-run AI Matching after updating your profile skills to view improved scoring.",
        ]

        response = SkillGapAnalysisResponse(
            total_analyzed_jobs=total_analyzed,
            candidate_skills_count=len(candidate_skills),
            most_requested_skills=most_requested,
            missing_skills=missing_items,
            emerging_skills=emerging_items[:8],
            recommendations=recommendations,
        )
        self._set_cached(uid_str, "skill_gap_analysis", response)
        return response

    async def generateAnalyticsSnapshot(
        self, user_id: Union[uuid.UUID, str]
    ) -> AnalyticsSnapshotModel:
        """
        Record a point-in-time analytical snapshot for trend monitoring.
        """
        uid = uuid.UUID(str(user_id))
        health = await self.calculateProfileHealth(uid)
        readiness = await self.calculateCareerReadiness(uid)
        match_stats = await self.analytics_repo.get_match_distribution(uid)

        snapshot_data = {
            "user_id": uid,
            "profile_score": health.overall_score,
            "readiness_score": readiness.career_readiness_score,
            "average_match_score": match_stats["avg_score"],
            "excellent_matches": match_stats["excellent"],
            "strong_matches": match_stats["strong"],
            "moderate_matches": match_stats["moderate"],
            "weak_matches": match_stats["weak"],
            "created_at": datetime.now(timezone.utc),
        }

        snapshot = await self.analytics_repo.create_snapshot(snapshot_data)
        self.invalidate_user_cache(uid)
        return snapshot

    async def generateDashboard(
        self, user_id: Union[uuid.UUID, str]
    ) -> DashboardOverviewResponse:
        """
        Generate full dashboard overview with KPI summary cards, trends, and top 10 matches.
        """
        start_time = time.perf_counter()
        uid = uuid.UUID(str(user_id))

        total_available_jobs = await self.analytics_repo.get_total_jobs_available()
        match_stats = await self.analytics_repo.get_match_distribution(uid)
        top_matches_records = await self.analytics_repo.get_top_matches(uid, limit=10)

        health = await self.calculateProfileHealth(uid)
        readiness = await self.calculateCareerReadiness(uid)

        # Get latest historical snapshot for delta trends
        latest_snapshot = await self.analytics_repo.get_latest_snapshot(uid)

        if latest_snapshot:
            match_delta = round(match_stats["avg_score"] - latest_snapshot.average_match_score, 1)
            jobs_delta = match_stats["total"] - (
                latest_snapshot.excellent_matches
                + latest_snapshot.strong_matches
                + latest_snapshot.moderate_matches
                + latest_snapshot.weak_matches
            )
            profile_delta = round(health.overall_score - latest_snapshot.profile_score, 1)
            readiness_delta = round(readiness.career_readiness_score - latest_snapshot.readiness_score, 1)
        else:
            # Baseline trends
            match_delta = 0.0
            jobs_delta = match_stats["total"]
            profile_delta = 0.0
            readiness_delta = 0.0
            # Auto-create initial snapshot if none exists
            if match_stats["total"] > 0:
                try:
                    await self.generateAnalyticsSnapshot(uid)
                except Exception:
                    pass

        # Format Top 10 Matches
        top_matches_list: List[MatchInsightItem] = []
        for m in top_matches_records:
            if m.job:
                top_matches_list.append(
                    MatchInsightItem(
                        job_id=m.job_id,
                        job_title=m.job.title,
                        company=m.job.company,
                        match_score=round(m.overall_score, 1),
                        location=m.job.location,
                        source=m.job.source,
                        posted_date=m.job.posted_at,
                        employment_type=m.job.employment_type,
                        salary_min=float(m.job.salary_min) if m.job.salary_min is not None else None,
                        salary_max=float(m.job.salary_max) if m.job.salary_max is not None else None,
                        currency=m.job.currency or "USD",
                        apply_url=m.job.apply_url,
                        company_website=m.job.company_website,
                        missing_skills=m.missing_skills or [],
                        is_saved=False,
                    )
                )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return DashboardOverviewResponse(
            total_jobs=total_available_jobs,
            jobs_matched=match_stats["total"],
            average_match_score=match_stats["avg_score"],
            excellent_matches=match_stats["excellent"],
            strong_matches=match_stats["strong"],
            moderate_matches=match_stats["moderate"],
            weak_matches=match_stats["weak"],
            trends=DashboardTrends(
                match_score_delta=match_delta,
                jobs_matched_delta=jobs_delta,
                profile_score_delta=profile_delta,
                readiness_delta=readiness_delta,
            ),
            top_matches=top_matches_list,
            profile_score=health.overall_score,
            readiness_score=readiness.career_readiness_score,
            latency_ms=elapsed_ms,
            generated_at=datetime.now(timezone.utc),
        )

    async def getAnalytics(
        self, user_id: Union[uuid.UUID, str]
    ) -> AnalyticsDashboardResponse:
        """
        Aggregate interactive chart datasets for Recharts visualizations:
        1. Match Distribution
        2. Top Skills Demand
        3. Missing Skills Frequency
        4. Location Distribution
        5. Profile Progress Snapshots
        """
        start_time = time.perf_counter()
        uid = uuid.UUID(str(user_id))

        match_stats = await self.analytics_repo.get_match_distribution(uid)
        total_matches = match_stats["total"]
        denom = max(1, total_matches)

        # 1. Match Distribution
        match_distribution_items = [
            DistributionItem(
                name="Excellent (85%+)",
                value=match_stats["excellent"],
                color="#10b981",  # Emerald
                percentage=round((match_stats["excellent"] / denom) * 100.0, 1),
            ),
            DistributionItem(
                name="Strong (70-84%)",
                value=match_stats["strong"],
                color="#3b82f6",  # Blue
                percentage=round((match_stats["strong"] / denom) * 100.0, 1),
            ),
            DistributionItem(
                name="Moderate (50-69%)",
                value=match_stats["moderate"],
                color="#f59e0b",  # Amber
                percentage=round((match_stats["moderate"] / denom) * 100.0, 1),
            ),
            DistributionItem(
                name="Weak (<50%)",
                value=match_stats["weak"],
                color="#ef4444",  # Red
                percentage=round((match_stats["weak"] / denom) * 100.0, 1),
            ),
        ]

        match_distribution_data = MatchDistributionData(
            excellent=match_stats["excellent"],
            strong=match_stats["strong"],
            moderate=match_stats["moderate"],
            weak=match_stats["weak"],
            total=total_matches,
            items=match_distribution_items,
        )

        # 2 & 3. Top Skills and Missing Skills
        skill_analysis = await self.generateSkillGapAnalysis(uid)

        top_skills_chart: List[TopSkillDemandItem] = [
            TopSkillDemandItem(
                name=s.name,
                demand=s.count,
                value_score=round(s.percentage, 1),
            )
            for s in skill_analysis.most_requested_skills[:10]
        ]

        missing_skills_chart: List[MissingSkillItem] = [
            MissingSkillItem(
                name=m.name,
                frequency=m.count,
                importance=m.priority or "Medium",
            )
            for m in skill_analysis.missing_skills[:10]
        ]

        # 4. Location Distribution (Remote, Hybrid, Onsite)
        matches = await self.analytics_repo.get_all_matches_with_jobs(uid, limit=200)
        remote_count = 0
        hybrid_count = 0
        onsite_count = 0

        for m in matches:
            if m.job and m.job.location:
                loc = m.job.location.lower()
                if "remote" in loc or "anywhere" in loc:
                    remote_count += 1
                elif "hybrid" in loc:
                    hybrid_count += 1
                else:
                    onsite_count += 1
            else:
                remote_count += 1

        loc_total = max(1, remote_count + hybrid_count + onsite_count)
        location_distribution = [
            LocationDistributionItem(
                type="Remote",
                count=remote_count,
                percentage=round((remote_count / loc_total) * 100.0, 1),
            ),
            LocationDistributionItem(
                type="Hybrid",
                count=hybrid_count,
                percentage=round((hybrid_count / loc_total) * 100.0, 1),
            ),
            LocationDistributionItem(
                type="Onsite",
                count=onsite_count,
                percentage=round((onsite_count / loc_total) * 100.0, 1),
            ),
        ]

        # 5. Profile Progress Snapshots
        snapshots = await self.analytics_repo.get_snapshots(uid, limit=20)
        profile_progress: List[AnalyticsSnapshotItem] = []

        if snapshots:
            for s in snapshots:
                profile_progress.append(
                    AnalyticsSnapshotItem(
                        id=s.id,
                        timestamp=s.created_at,
                        profile_score=round(s.profile_score, 1),
                        readiness_score=round(s.readiness_score, 1),
                        average_match_score=round(s.average_match_score, 1),
                        excellent_matches=s.excellent_matches,
                        strong_matches=s.strong_matches,
                        moderate_matches=s.moderate_matches,
                        weak_matches=s.weak_matches,
                    )
                )
        else:
            # Provide initial baseline data point from current calculation
            health = await self.calculateProfileHealth(uid)
            readiness = await self.calculateCareerReadiness(uid)
            profile_progress.append(
                AnalyticsSnapshotItem(
                    id=uuid.uuid4(),
                    timestamp=datetime.now(timezone.utc),
                    profile_score=health.overall_score,
                    readiness_score=readiness.career_readiness_score,
                    average_match_score=match_stats["avg_score"],
                    excellent_matches=match_stats["excellent"],
                    strong_matches=match_stats["strong"],
                    moderate_matches=match_stats["moderate"],
                    weak_matches=match_stats["weak"],
                )
            )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return AnalyticsDashboardResponse(
            match_distribution=match_distribution_data,
            top_skills=top_skills_chart,
            missing_skills=missing_skills_chart,
            location_distribution=location_distribution,
            profile_progress=profile_progress,
            latency_ms=elapsed_ms,
            generated_at=datetime.now(timezone.utc),
        )
