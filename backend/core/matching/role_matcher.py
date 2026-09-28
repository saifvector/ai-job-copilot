"""
Role Matcher Module for Phase 5 AI Job Matching Engine.
Compares candidate's preferred roles and past titles with the job title.
"""
from dataclasses import dataclass
from typing import Optional
from core.matching.base import CandidateProfileDTO, JobProfileDTO
from core.matching.semantic import SemanticMatcher, default_semantic_matcher


@dataclass
class RoleMatchResult:
    score: float
    matched_role: Optional[str] = None


class RoleMatcher:
    """
    Evaluates alignment between Candidate preferred roles and the Job posting title.
    Leverages semantic similarity and domain role mappings.
    """

    def __init__(self, semantic_matcher: Optional[SemanticMatcher] = None):
        self.semantic_matcher = semantic_matcher or default_semantic_matcher

    def match(self, candidate: CandidateProfileDTO, job: JobProfileDTO) -> RoleMatchResult:
        preferred_roles = [r.strip() for r in candidate.preferred_roles if r.strip()]

        # If candidate specified no preferred roles, use past experience roles as fallback
        if not preferred_roles:
            preferred_roles = [
                exp.get("role", "").strip()
                for exp in candidate.experiences
                if isinstance(exp, dict) and exp.get("role")
            ]

        # If still no roles available, neutral baseline score
        if not preferred_roles:
            return RoleMatchResult(score=75.0, matched_role=None)

        job_title = job.title.strip()
        best_role: Optional[str] = None
        best_sim = 0.0

        for role in preferred_roles:
            sim = self.semantic_matcher.get_similarity(role, job_title)
            if sim > best_sim:
                best_sim = sim
                best_role = role

        # Convert similarity to 0-100 scale with graceful scaling
        if best_sim >= 0.85:
            # Strong alignment (e.g. AI Engineer vs Machine Learning Engineer)
            score = 85.0 + (best_sim - 0.85) * 100.0  # Scales from 85 to 100
        elif best_sim >= 0.50:
            # Moderate alignment
            score = 60.0 + (best_sim - 0.50) * 70.0   # Scales from 60 to 84.5
        elif best_sim >= 0.30:
            score = 40.0 + (best_sim - 0.30) * 100.0
        else:
            score = max(15.0, best_sim * 100.0)

        score = min(100.0, max(0.0, score))

        return RoleMatchResult(
            score=round(score, 1),
            matched_role=best_role if best_sim >= 0.50 else None,
        )
