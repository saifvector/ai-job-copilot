"""
Base Data Transfer Objects and Configuration for AI Job Matching Engine.
"""
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from core.config import settings


@dataclass
class ScoringWeights:
    """
    Configurable weights for job matching criteria.
    Defaults: Skills 50%, Experience 20%, Role Alignment 15%, Location 10%, Education 5%.
    """
    skill_weight: float = field(default_factory=lambda: settings.MATCH_WEIGHT_SKILLS)
    experience_weight: float = field(default_factory=lambda: settings.MATCH_WEIGHT_EXPERIENCE)
    role_weight: float = field(default_factory=lambda: settings.MATCH_WEIGHT_ROLE)
    location_weight: float = field(default_factory=lambda: settings.MATCH_WEIGHT_LOCATION)
    education_weight: float = field(default_factory=lambda: settings.MATCH_WEIGHT_EDUCATION)

    def normalize(self) -> "ScoringWeights":
        """Normalize weights to guarantee total sum equals 1.0."""
        total = (
            self.skill_weight +
            self.experience_weight +
            self.role_weight +
            self.location_weight +
            self.education_weight
        )
        if total <= 0:
            return ScoringWeights(0.50, 0.20, 0.15, 0.10, 0.05)
        return ScoringWeights(
            skill_weight=self.skill_weight / total,
            experience_weight=self.experience_weight / total,
            role_weight=self.role_weight / total,
            location_weight=self.location_weight / total,
            education_weight=self.education_weight / total,
        )


@dataclass
class CandidateProfileDTO:
    """Consolidated candidate profile representation for matching."""
    user_id: uuid.UUID
    preferred_roles: List[str] = field(default_factory=list)
    preferred_locations: List[str] = field(default_factory=list)
    years_of_experience: int = 0
    skills: List[str] = field(default_factory=list)
    skill_confidences: Dict[str, float] = field(default_factory=dict)
    experiences: List[Dict[str, Any]] = field(default_factory=list)
    educations: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    summary: Optional[str] = None


@dataclass
class JobProfileDTO:
    """Job listing data representation for matching."""
    id: uuid.UUID
    title: str
    company: str
    location: str
    employment_type: Optional[str] = None
    description: str = ""
    requirements: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = "USD"
    source: str = ""
    apply_url: str = ""


@dataclass
class MatchBreakdownDTO:
    """Detailed score breakdown and AI gap analysis for a single job."""
    job_id: uuid.UUID
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    location_score: float
    role_score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
