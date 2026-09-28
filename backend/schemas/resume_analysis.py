import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.alias_generators import to_camel

from schemas.certification import CertificationResponse
from schemas.education import EducationResponse
from schemas.experience import ExperienceResponse
from schemas.project import ProjectResponse
from schemas.skill import SkillResponse, SKILL_CATEGORIES


class CandidateContact(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=255, example="Alex Chen")
    email: Optional[str] = Field(default=None, example="alex.chen@example.com")
    phone: Optional[str] = Field(default=None, example="+1 (555) 019-2834")


class RawParsedSkill(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(default="Other")
    confidence_score: Optional[float] = Field(default=0.9)

    @field_validator("confidence_score", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> float:
        if v is None:
            return 0.9
        try:
            val = float(v)
            if val > 1.0 and val <= 100.0:
                val = val / 100.0
            return max(0.1, min(1.0, round(val, 2)))
        except (ValueError, TypeError):
            return 0.9

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: Optional[str]) -> str:
        if not v:
            return "Other"
        v_str = str(v).strip()
        for cat in SKILL_CATEGORIES:
            if cat.lower() == v_str.lower():
                return cat
        # Fuzzy category mapping
        lower = v_str.lower()
        if "lang" in lower or "code" in lower:
            return "Programming Language"
        elif "framework" in lower or "library" in lower or "react" in lower or "angular" in lower or "vue" in lower:
            return "Framework"
        elif "data" in lower or "sql" in lower or "db" in lower or "postgres" in lower or "mongo" in lower:
            return "Database"
        elif "ai" in lower or "ml" in lower or "learning" in lower or "nlp" in lower or "llm" in lower:
            return "AI/ML"
        elif "tool" in lower or "git" in lower or "docker" in lower or "kubernetes" in lower or "devops" in lower or "ci/cd" in lower:
            return "Tool"
        elif "cloud" in lower or "aws" in lower or "gcp" in lower or "azure" in lower:
            return "Cloud"
        return "Other"



class RawParsedProject(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str = Field(..., min_length=1)
    description: Optional[str] = Field(default="")
    technologies: Optional[List[str]] = Field(default_factory=list)

    @field_validator("technologies", mode="before")
    @classmethod
    def normalize_technologies(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [t.strip() for t in v.split(",") if t.strip()]
        elif isinstance(v, list):
            return [str(t).strip() for t in v if str(t).strip()]
        return []


class RawParsedEducation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    institution: str = Field(..., min_length=1)
    degree: str = Field(..., min_length=1)
    field_of_study: Optional[str] = Field(default=None)
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)


class RawParsedExperience(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    company: str = Field(..., min_length=1)
    role: str = Field(..., min_length=1)
    description: Optional[str] = Field(default="")
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)


class RawParsedCertification(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str = Field(..., min_length=1)
    issuer: str = Field(..., min_length=1)
    issue_date: Optional[str] = Field(default=None)


class ParsedResumeExtraction(BaseModel):
    """
    Validation schema for raw Gemini LLM JSON response.
    Enforces strict typing, defaults, and clean normalization.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: Optional[str] = Field(default="")
    email: Optional[str] = Field(default="")
    phone: Optional[str] = Field(default="")
    summary: Optional[str] = Field(default="")
    skills: List[RawParsedSkill] = Field(default_factory=list)
    projects: List[RawParsedProject] = Field(default_factory=list)
    education: List[RawParsedEducation] = Field(default_factory=list)
    experience: List[RawParsedExperience] = Field(default_factory=list)
    certifications: List[RawParsedCertification] = Field(default_factory=list)


class ProfileSummaryResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_id: uuid.UUID
    summary: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResumeParseResponse(BaseModel):
    """
    Standard response returned after successful resume text extraction & AI processing.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_id: uuid.UUID
    candidate: CandidateContact
    summary: str
    skills: List[SkillResponse]
    projects: List[ProjectResponse]
    education: List[EducationResponse]
    experience: List[ExperienceResponse]
    certifications: List[CertificationResponse]
    model_used: str
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
