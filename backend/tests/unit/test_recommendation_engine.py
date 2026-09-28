import pytest
from services.recommendation_engine import CareerRecommendationEngine


def test_recommendation_engine_skill_prioritization():
    analytics_summary = {
        "total_applications": 20,
        "interview_rate": 0.25,
        "offer_rate": 0.05,
    }
    resume_performances = [
        {"resume_title": "Fullstack Resume", "response_rate": 0.35, "applications_sent": 10, "interviews_received": 3, "ats_score": 88.0},
        {"resume_title": "Generic Resume", "response_rate": 0.10, "applications_sent": 10, "interviews_received": 1, "ats_score": 72.0},
    ]
    skill_impacts = [
        {"skill_name": "FastAPI", "interviews_influenced": 4, "offers_influenced": 1, "average_match_score": 89.5, "sample_size": 8},
        {"skill_name": "Kubernetes", "interviews_influenced": 3, "offers_influenced": 1, "average_match_score": 85.0, "sample_size": 6},
        {"skill_name": "Perl", "interviews_influenced": 0, "offers_influenced": 0, "average_match_score": 60.0, "sample_size": 4},
    ]
    company_metrics = [
        {"company": "Google", "applications_sent": 2, "interviews_count": 1, "response_rate": 0.5, "avg_response_days": 4.5},
    ]
    strategy_metrics = {
        "source_breakdown": [
            {"source": "Referral", "sent": 4, "interviews": 2, "response_rate": 0.50},
            {"source": "LinkedIn", "sent": 16, "interviews": 2, "response_rate": 0.125},
        ],
        "score_tier_breakdown": [
            {"tier": "80-89%", "sent": 8, "interviews": 3, "rate": 0.375},
            {"tier": "<60%", "sent": 5, "interviews": 0, "rate": 0.0},
        ],
    }

    recs = CareerRecommendationEngine.generate_recommendations(
        analytics_summary=analytics_summary,
        resume_performances=resume_performances,
        skill_impacts=skill_impacts,
        company_metrics=company_metrics,
        strategy_metrics=strategy_metrics,
    )

    assert len(recs) >= 4
    categories = [r.category for r in recs]
    assert "SKILL" in categories
    assert "RESUME" in categories
    assert "STRATEGY" in categories

    # Skill rec check
    skill_rec = next(r for r in recs if r.category == "SKILL" and "FastAPI" in r.title)
    assert "FastAPI" in skill_rec.description
    assert skill_rec.impact_level == "HIGH"
    assert skill_rec.confidence_score >= 0.85

    # Lagging skill rec check
    lagging_rec = next(r for r in recs if r.category == "SKILL" and "Perl" in r.title)
    assert "Perl" in lagging_rec.title
    assert lagging_rec.impact_level == "MEDIUM"

    # Resume rec check
    resume_rec = next(r for r in recs if r.category == "RESUME")
    assert "Standardize" in resume_rec.title or "ATS" in resume_rec.title

    # Strategy source check
    strat_rec = next(r for r in recs if r.category == "STRATEGY" and "Referral" in r.title)
    assert "Referral" in strat_rec.title
    assert strat_rec.impact_level == "HIGH"


def test_recommendation_engine_baseline_fallback():
    # Empty baseline
    recs = CareerRecommendationEngine.generate_recommendations(
        analytics_summary={"total_applications": 1, "interview_rate": 0.0, "offer_rate": 0.0},
        resume_performances=[],
        skill_impacts=[],
        company_metrics=[],
        strategy_metrics={},
    )
    assert len(recs) >= 2
    assert any("Baseline" in r.title or "Cadence" in r.title for r in recs)
