"""
Education Matcher Module for Phase 5 AI Job Matching Engine.
Compares candidate academic credentials with job educational requirements.
"""
import re
from dataclasses import dataclass
from typing import Optional, Tuple
from core.matching.base import CandidateProfileDTO, JobProfileDTO


@dataclass
class EducationMatchResult:
    score: float
    highest_degree: str
    field_of_study: Optional[str] = None


class EducationMatcher:
    """
    Evaluates degree level and field of study alignment against job expectations.
    """

    TECH_FIELDS = {
        "computer science", "cs", "software engineering", "artificial intelligence",
        "ai", "data science", "machine learning", "information technology", "it",
        "electrical engineering", "computer engineering", "mathematics", "statistics",
        "data analytics", "robotics", "computational linguistics",
    }

    def detect_degree_level(self, degree_str: str) -> Tuple[int, str]:
        """Returns (numeric_rank, canonical_name)."""
        d = degree_str.lower()
        if any(w in d for w in ["phd", "ph.d", "doctorate", "doctoral"]):
            return (4, "Doctorate")
        if any(w in d for w in ["master", "ms", "m.s", "mtech", "m.tech", "mca", "mba"]):
            return (3, "Master's")
        if any(w in d for w in ["bachelor", "btech", "b.tech", "bs", "b.s", "be", "b.e", "bca"]):
            return (2, "Bachelor's")
        if any(w in d for w in ["associate", "diploma", "bootcamp"]):
            return (1, "Associate / Certificate")
        return (0, "Unknown")

    def match(self, candidate: CandidateProfileDTO, job: JobProfileDTO) -> EducationMatchResult:
        highest_rank = 0
        canonical_degree = "None"
        best_field: Optional[str] = None
        has_tech_field = False

        for edu in candidate.educations:
            if not isinstance(edu, dict):
                continue
            deg_str = edu.get("degree", "")
            field_str = (edu.get("field_of_study") or "").lower()

            rank, name = self.detect_degree_level(deg_str)
            if rank > highest_rank:
                highest_rank = rank
                canonical_degree = name
                best_field = edu.get("field_of_study")

            if any(tf in field_str for tf in self.TECH_FIELDS):
                has_tech_field = True
                if not best_field:
                    best_field = edu.get("field_of_study")

        # Base score based on degree level
        if highest_rank == 4:     # Doctorate
            base_score = 100.0
        elif highest_rank == 3:   # Master's
            base_score = 95.0
        elif highest_rank == 2:   # Bachelor's
            base_score = 90.0
        elif highest_rank == 1:   # Associate / Certificate
            base_score = 75.0
        else:
            base_score = 65.0     # Self-taught or not specified

        # Adjust for STEM / tech field alignment
        if best_field:
            if has_tech_field:
                base_score = min(100.0, base_score + 5.0)
            else:
                base_score = max(50.0, base_score - 10.0)

        # Check job requirement constraints
        job_text = f"{job.requirements or ''} {job.description}".lower()
        if "phd required" in job_text or "ph.d. required" in job_text:
            if highest_rank < 4:
                base_score = min(base_score, 60.0)
        elif "master's required" in job_text or "masters required" in job_text:
            if highest_rank < 3:
                base_score = min(base_score, 75.0)

        return EducationMatchResult(
            score=round(base_score, 1),
            highest_degree=canonical_degree,
            field_of_study=best_field,
        )
