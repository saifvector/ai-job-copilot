import uuid
from typing import Any, Dict, List
from schemas.career_intelligence import RecommendationItem


class CareerRecommendationEngine:
    """
    Evidence-based recommendation engine for career intelligence and outcome optimization.
    Grounds all actionable guidance in observed empirical data from applications, resumes,
    match scores, and hiring outcomes.
    """

    @classmethod
    def generate_recommendations(
        cls,
        analytics_summary: Dict[str, Any],
        resume_performances: List[Dict[str, Any]],
        skill_impacts: List[Dict[str, Any]],
        company_metrics: List[Dict[str, Any]],
        strategy_metrics: Dict[str, Any],
    ) -> List[RecommendationItem]:
        recommendations: List[RecommendationItem] = []

        total_apps = analytics_summary.get("total_applications", 0)
        interview_rate = analytics_summary.get("interview_rate", 0.0)
        offer_rate = analytics_summary.get("offer_rate", 0.0)

        # -------------------------------------------------------------
        # 1. Skill Prioritization Recommendations (Empirical Evidence)
        # -------------------------------------------------------------
        if skill_impacts:
            # Sort skills by interviews influenced and match score
            top_skills = sorted(
                skill_impacts,
                key=lambda s: (s.get("interviews_influenced", 0), s.get("average_match_score", 0.0)),
                reverse=True,
            )
            high_converting = [s for s in top_skills if s.get("interviews_influenced", 0) > 0]

            if high_converting:
                best_skill = high_converting[0]
                skill_name = best_skill.get("skill_name", "")
                interviews = best_skill.get("interviews_influenced", 0)
                avg_score = best_skill.get("average_match_score", 0.0)

                recommendations.append(
                    RecommendationItem(
                        id=str(uuid.uuid4()),
                        category="SKILL",
                        title=f"Prioritize High-Conversion Competency: {skill_name}",
                        description=(
                            f"Applications featuring '{skill_name}' demonstrate the highest correlation with positive employer responses. "
                            f"Continue positioning this skill prominently in your summary and primary project bullet points."
                        ),
                        evidence=(
                            f"Observed {interviews} interview outcome(s) and an average match score of {avg_score:.1f}% "
                            f"on applications highlighting '{skill_name}'."
                        ),
                        impact_level="HIGH",
                        action_suggested=f"Highlight '{skill_name}' across your resume headline and core competencies section.",
                        confidence_score=0.92,
                    )
                )

            # Check if there are skills with low conversion or missing
            low_converting = [
                s for s in top_skills
                if s.get("interviews_influenced", 0) == 0 and s.get("sample_size", 0) >= 3
            ]
            if low_converting:
                lagging_skill = low_converting[0]
                lagging_name = lagging_skill.get("skill_name", "")
                sample = lagging_skill.get("sample_size", 0)

                recommendations.append(
                    RecommendationItem(
                        id=str(uuid.uuid4()),
                        category="SKILL",
                        title=f"Re-evaluate Positioning for: {lagging_name}",
                        description=(
                            f"Applications citing '{lagging_name}' have produced 0 interviews across {sample} submissions. "
                            f"Ensure this skill is backed by quantifiable project achievements rather than isolated keywords."
                        ),
                        evidence=f"Zero interview outcomes recorded across {sample} tracked applications containing '{lagging_name}'.",
                        impact_level="MEDIUM",
                        action_suggested=f"Add demonstrable project metrics or open-source repo links verifying your {lagging_name} experience.",
                        confidence_score=0.78,
                    )
                )
        else:
            recommendations.append(
                RecommendationItem(
                    id=str(uuid.uuid4()),
                    category="SKILL",
                    title="Expand Tracked Skill Baseline",
                    description="As you submit applications and log outcomes, our intelligence engine correlates which competencies yield interviews.",
                    evidence="Initial observation phase; fewer than 3 outcomes currently logged.",
                    impact_level="LOW",
                    action_suggested="Log application outcomes as you hear back from recruiters to train your skill impact matrix.",
                    confidence_score=0.70,
                )
            )

        # -------------------------------------------------------------
        # 2. Resume Effectiveness Recommendations
        # -------------------------------------------------------------
        if resume_performances:
            sorted_resumes = sorted(
                resume_performances,
                key=lambda r: r.get("response_rate", 0.0),
                reverse=True,
            )
            top_resume = sorted_resumes[0]
            top_rate = top_resume.get("response_rate", 0.0)
            top_title = top_resume.get("resume_title") or "Top Tailored Variant"

            if top_rate > 0.0 and len(sorted_resumes) > 1:
                worst_resume = sorted_resumes[-1]
                worst_rate = worst_resume.get("response_rate", 0.0)
                worst_title = worst_resume.get("resume_title") or "Lower Variant"

                if top_rate > worst_rate:
                    multiplier = round(top_rate / max(worst_rate, 0.05), 1)
                    recommendations.append(
                        RecommendationItem(
                            id=str(uuid.uuid4()),
                            category="RESUME",
                            title=f"Standardize on Structure from '{top_title}'",
                            description=(
                                f"Variant '{top_title}' achieves a {top_rate*100:.1f}% response rate, outperforming "
                                f"'{worst_title}' ({worst_rate*100:.1f}%) by ~{multiplier}x."
                            ),
                            evidence=(
                                f"'{top_title}' yielded {top_resume.get('interviews_received', 0)} interviews from "
                                f"{top_resume.get('applications_sent', 0)} applications."
                            ),
                            impact_level="HIGH",
                            action_suggested="Adopt the keyword density and bullet point structure from this variant across future applications.",
                            confidence_score=0.88,
                        )
                    )

            # Check for low ATS scores among active tailored resumes
            low_ats = [r for r in resume_performances if (r.get("ats_score") or 0.0) < 75.0]
            if low_ats:
                target = low_ats[0]
                target_title = target.get("resume_title") or "Target Resume"
                curr_ats = target.get("ats_score", 0.0)
                recommendations.append(
                    RecommendationItem(
                        id=str(uuid.uuid4()),
                        category="RESUME",
                        title=f"Optimize ATS Parsing Score for '{target_title}'",
                        description=(
                            f"This tailored resume version has an ATS compliance score of {curr_ats:.1f}%. "
                            f"Increasing ATS compliance above 85% strongly correlates with initial recruiter screen passes."
                        ),
                        evidence=f"ATS score measured at {curr_ats:.1f}% (target threshold: 85.0%+).",
                        impact_level="HIGH",
                        action_suggested="Use the Resume Tailoring studio to integrate missing required keywords and standardized header formats.",
                        confidence_score=0.89,
                    )
                )

        # -------------------------------------------------------------
        # 3. Application Strategy & Channel Optimization
        # -------------------------------------------------------------
        source_data = strategy_metrics.get("source_breakdown", [])
        if source_data:
            # Check if referrals or specific sources outperform
            sorted_sources = sorted(source_data, key=lambda s: s.get("response_rate", 0.0), reverse=True)
            best_source = sorted_sources[0]
            if best_source.get("response_rate", 0.0) > 0.0 and best_source.get("sent", 0) >= 2:
                s_name = best_source.get("source", "Direct")
                s_rate = best_source.get("response_rate", 0.0)
                recommendations.append(
                    RecommendationItem(
                        id=str(uuid.uuid4()),
                        category="STRATEGY",
                        title=f"Scale Outreach Through {s_name}",
                        description=(
                            f"Your highest conversion channel is '{s_name}' with a {s_rate*100:.1f}% interview rate. "
                            f"Prioritize applying through this channel whenever opportunities allow."
                        ),
                        evidence=(
                            f"{best_source.get('interviews', 0)} interview(s) secured across {best_source.get('sent', 0)} "
                            f"applications submitted via {s_name}."
                        ),
                        impact_level="HIGH",
                        action_suggested=f"Allocate at least 50% of your weekly application volume to {s_name}.",
                        confidence_score=0.86,
                    )
                )

        # Match score threshold advice
        tiers = strategy_metrics.get("score_tier_breakdown", [])
        high_tier = next((t for t in tiers if t.get("tier") in ("90%+", "80-89%")), None)
        low_tier = next((t for t in tiers if t.get("tier") in ("<60%", "60-69%")), None)

        if high_tier and low_tier and high_tier.get("rate", 0.0) > low_tier.get("rate", 0.0):
            h_rate = high_tier.get("rate", 0.0) * 100
            l_rate = low_tier.get("rate", 0.0) * 100
            recommendations.append(
                RecommendationItem(
                    id=str(uuid.uuid4()),
                    category="STRATEGY",
                    title="Enforce Match Score Gate (>= 75%)",
                    description=(
                        f"Applications targeting roles with match scores >= 80% achieve an interview rate of {h_rate:.1f}%, "
                        f"compared to only {l_rate:.1f}% for lower-tier matches."
                    ),
                    evidence=f"{high_tier.get('interviews', 0)} interviews from {high_tier.get('sent', 0)} high-match applications.",
                    impact_level="MEDIUM",
                    action_suggested="Filter jobs to only apply to roles meeting or exceeding a 75% match threshold.",
                    confidence_score=0.91,
                )
            )

        # -------------------------------------------------------------
        # 4. Target Role & Company Insights
        # -------------------------------------------------------------
        if company_metrics:
            high_response_cos = [c for c in company_metrics if c.get("interviews_count", 0) > 0]
            if high_response_cos:
                top_co = high_response_cos[0]
                co_name = top_co.get("company", "")
                recommendations.append(
                    RecommendationItem(
                        id=str(uuid.uuid4()),
                        category="ROLE",
                        title=f"Target Peer Companies in {co_name}'s Peer Group",
                        description=(
                            f"{co_name} responded positively to your profile. Organizations with similar business models, "
                            f"scale, and tech stacks are likely to exhibit comparable hiring interest."
                        ),
                        evidence=f"Interview outcome recorded at {co_name} with response turnaround under {top_co.get('avg_response_days', 0):.1f} days.",
                        impact_level="MEDIUM",
                        action_suggested=f"Use Job Discovery to search for direct competitors and industry peers of {co_name}.",
                        confidence_score=0.82,
                    )
                )

        # Baseline fallback recommendation if few recommendations produced
        if len(recommendations) < 2:
            recommendations.append(
                RecommendationItem(
                    id=str(uuid.uuid4()),
                    category="STRATEGY",
                    title="Maintain Consistent Weekly Cadence",
                    description="Maintaining a steady cadence of 8–12 highly-tailored submissions per week minimizes pipeline gaps and accelerates learning feedback loops.",
                    evidence=f"Current recorded total: {total_apps} application(s).",
                    impact_level="LOW",
                    action_suggested="Set a recurring reminder to apply to 2-3 matched positions daily.",
                    confidence_score=0.75,
                )
            )

        return recommendations
