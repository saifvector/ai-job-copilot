"""
Experience Matcher Module for Phase 5 AI Job Matching Engine.
Compares candidate years, past role titles, and technology usage against job requirements.
"""
import re
from dataclasses import dataclass
from typing import Optional
from core.matching.base import CandidateProfileDTO, JobProfileDTO


@dataclass
class ExperienceMatchResult:
    score: float
    candidate_years: int
    required_years: int
    seniority_aligned: bool


class ExperienceMatcher:
    """
    Evaluates Candidate experience level against Job expectations.
    Considers years of experience, seniority keywords, and domain background.
    """

    YEARS_PATTERN = re.compile(
        r"(\d+)\+?\s*(?:-\s*(\d+))?\s*(?:years?|yrs?)(?:\s+of)?\s+experience",
        re.IGNORECASE,
    )

    def extract_required_years(self, job: JobProfileDTO) -> int:
        """Parse minimum required years from description, requirements, or title."""
        full_text = f"{job.title} {job.requirements or ''} {job.description}"

        matches = self.YEARS_PATTERN.findall(full_text)
        if matches:
            try:
                first_match = matches[0]
                min_years = int(first_match[0])
                if min_years > 0:
                    return min_years
            except (ValueError, IndexError):
                pass

        # Infer from title seniority keywords
        title_lower = job.title.lower()
        if any(w in title_lower for w in ["principal", "staff", "director", "architect"]):
            return 7
        if any(w in title_lower for w in ["lead", "manager"]):
            return 6
        if any(w in title_lower for w in ["senior", "sr.", "sr "]):
            return 4
        if any(w in title_lower for w in ["mid-level", "intermediate"]):
            return 3
        if any(w in title_lower for w in ["junior", "jr.", "entry", "associate"]):
            return 1
        if "intern" in title_lower:
            return 0

        # General industry baseline
        return 2

    def match(self, candidate: CandidateProfileDTO, job: JobProfileDTO) -> ExperienceMatchResult:
        candidate_years = candidate.years_of_experience
        if candidate_years == 0 and candidate.experiences:
            # Fallback: each experience entry roughly accounts for at least 1 year
            candidate_years = max(1, len(candidate.experiences))

        required_years = self.extract_required_years(job)

        # 1. Years score (50% of experience evaluation)
        if required_years <= 0:
            years_score = 100.0
        elif candidate_years >= required_years:
            # Bonus points for solid experience, capped at 100
            years_score = 100.0
        else:
            ratio = candidate_years / required_years
            years_score = max(20.0, ratio * 100.0)

        # 2. Domain & past roles overlap (30% of experience evaluation)
        past_role_titles = [
            exp.get("role", "").lower()
            for exp in candidate.experiences
            if isinstance(exp, dict) and exp.get("role")
        ]
        job_title_tokens = set(re.findall(r"\w+", job.title.lower()))

        title_overlap = False
        for past_title in past_role_titles:
            past_tokens = set(re.findall(r"\w+", past_title))
            if job_title_tokens.intersection(past_tokens):
                title_overlap = True
                break

        domain_score = 95.0 if title_overlap else (75.0 if past_role_titles else 60.0)

        # 3. Seniority alignment (20% of experience evaluation)
        title_lower = job.title.lower()
        is_senior_job = any(w in title_lower for w in ["senior", "lead", "staff", "principal", "architect"])
        is_senior_candidate = candidate_years >= 4

        if is_senior_job:
            seniority_aligned = is_senior_candidate
            seniority_score = 100.0 if is_senior_candidate else 50.0
        else:
            seniority_aligned = True
            seniority_score = 95.0

        overall_exp_score = (
            0.50 * years_score +
            0.30 * domain_score +
            0.20 * seniority_score
        )

        return ExperienceMatchResult(
            score=round(min(100.0, max(0.0, overall_exp_score)), 1),
            candidate_years=candidate_years,
            required_years=required_years,
            seniority_aligned=seniority_aligned,
        )
