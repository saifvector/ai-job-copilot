"""
Pydantic Schemas for Phase 7 AI Resume Tailoring Engine API.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class KeywordAnalysisDTO(BaseModel):
    """Keyword alignment metrics extracted from target job description."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    matched_keywords: List[str] = Field(default_factory=list, alias="matchedKeywords")
    missing_keywords: List[str] = Field(default_factory=list, alias="missingKeywords")
    coverage_percentage: float = Field(alias="coveragePercentage")
    required_skills: List[str] = Field(default_factory=list, alias="requiredSkills")
    preferred_skills: List[str] = Field(default_factory=list, alias="preferredSkills")
    technologies: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class ATSScoreBreakdownDTO(BaseModel):
    """Detailed ATS scoring factors (0-100 scale)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    overall_score: float = Field(alias="overallScore")
    keyword_match: float = Field(alias="keywordMatch")
    skill_match: float = Field(alias="skillMatch")
    section_quality: float = Field(alias="sectionQuality")
    experience_relevance: float = Field(alias="experienceRelevance")
    formatting_structure: float = Field(alias="formattingStructure")
    suggestions: List[str] = Field(default_factory=list)


class ResumeSectionExperience(BaseModel):
    """Tailored employment history entry."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = None
    company: str
    role: str
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")
    description: str
    bullet_points: List[str] = Field(default_factory=list, alias="bulletPoints")
    highlighted_keywords: List[str] = Field(default_factory=list, alias="highlightedKeywords")


class ResumeSectionSkillGroup(BaseModel):
    """Categorized technical and professional skills."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    category: str
    skills: List[str] = Field(default_factory=list)


class ResumeSectionProject(BaseModel):
    """Technical project representation."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = None
    title: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    bullet_points: List[str] = Field(default_factory=list, alias="bulletPoints")


class ResumeSectionEducation(BaseModel):
    """Academic record representation."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = None
    institution: str
    degree: str
    field_of_study: Optional[str] = Field(default=None, alias="fieldOfStudy")
    start_date: Optional[str] = Field(default=None, alias="startDate")
    end_date: Optional[str] = Field(default=None, alias="endDate")


class ResumeSectionCertification(BaseModel):
    """Professional accreditation representation."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: Optional[str] = None
    name: str
    issuer: str
    issue_date: Optional[str] = Field(default=None, alias="issueDate")


class ResumeVersionDTO(BaseModel):
    """Specific optimized format variation of the resume (ATS, Recruiter, Balanced)."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    version_type: Literal["ats", "recruiter", "balanced"] = Field(alias="versionType")
    label: str
    summary: str
    skills: List[ResumeSectionSkillGroup] = Field(default_factory=list)
    experience: List[ResumeSectionExperience] = Field(default_factory=list)
    education: List[ResumeSectionEducation] = Field(default_factory=list)
    projects: List[ResumeSectionProject] = Field(default_factory=list)
    certifications: List[ResumeSectionCertification] = Field(default_factory=list)


class TailoredResumeCreateRequest(BaseModel):
    """Payload to request resume tailoring for a target job."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    job_id: uuid.UUID = Field(alias="jobId")
    resume_id: Optional[uuid.UUID] = Field(default=None, alias="resumeId")
    target_version: Optional[str] = Field(default="balanced", alias="targetVersion")
    custom_instructions: Optional[str] = Field(default=None, alias="customInstructions")


class TailoredResumeResponse(BaseModel):
    """Full tailored resume entity with multiple versions, ATS score, and analysis."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID = Field(alias="userId")
    job_id: uuid.UUID = Field(alias="jobId")
    original_resume_id: Optional[uuid.UUID] = Field(default=None, alias="originalResumeId")

    title: str
    summary: str
    ats_score: float = Field(alias="atsScore")
    keyword_coverage: float = Field(alias="keywordCoverage")

    versions: Dict[str, ResumeVersionDTO] = Field(default_factory=dict)
    keyword_analysis: KeywordAnalysisDTO = Field(alias="keywordAnalysis")
    ats_breakdown: ATSScoreBreakdownDTO = Field(alias="atsBreakdown")
    recommendations: List[str] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class TailoredResumeListItem(BaseModel):
    """Summary item for tailored resumes listing view."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID = Field(alias="userId")
    job_id: uuid.UUID = Field(alias="jobId")
    job_title: str = Field(alias="jobTitle")
    job_company: str = Field(alias="jobCompany")
    title: str
    ats_score: float = Field(alias="atsScore")
    keyword_coverage: float = Field(alias="keywordCoverage")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
