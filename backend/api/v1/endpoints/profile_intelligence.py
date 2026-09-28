"""
Profile Intelligence API Endpoints for Candidate Skills, Projects, Experience, and Summary.
Provides structured access to AI-extracted resume intelligence.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from core.dependencies import (
    get_certification_repository,
    get_current_user_id,
    get_education_repository,
    get_experience_repository,
    get_profile_repository,
    get_project_repository,
    get_skill_repository,
    get_user_repository,
)
from repositories.candidate_intelligence_repository import (
    CertificationRepository,
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.profile_repository import ProfileRepository
from repositories.user_repository import UserRepository
from schemas.certification import CertificationResponse
from schemas.common import ApiResponse
from schemas.education import EducationResponse
from schemas.experience import ExperienceResponse
from schemas.project import ProjectResponse
from schemas.resume_analysis import CandidateContact, ProfileSummaryResponse, ResumeParseResponse
from schemas.skill import SkillResponse

router = APIRouter()


@router.get(
    "/summary",
    response_model=ApiResponse[ProfileSummaryResponse],
    summary="Get Candidate Professional Summary",
    description="Retrieve the AI-generated executive profile summary for the current candidate.",
)
async def get_profile_summary(
    user_id: uuid.UUID = Depends(get_current_user_id),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
) -> ApiResponse[ProfileSummaryResponse]:
    profile = await profile_repo.get_by_user_id(user_id)
    summary_text = profile.summary if (profile and profile.summary) else ""
    return ApiResponse(
        data=ProfileSummaryResponse(
            user_id=user_id,
            summary=summary_text,
            updated_at=profile.updated_at if profile else None,
        ),
        message="Profile summary retrieved successfully.",
    )


@router.get(
    "/skills",
    response_model=ApiResponse[List[SkillResponse]],
    summary="Get Extracted Candidate Skills",
    description="Retrieve all verified candidate skills, optionally filtered by category.",
)
async def get_profile_skills(
    category: Optional[str] = Query(default=None, description="Filter skills by category"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    skill_repo: SkillRepository = Depends(get_skill_repository),
) -> ApiResponse[List[SkillResponse]]:
    skills = await skill_repo.get_by_user_id(user_id)
    if category:
        skills = [s for s in skills if s.category.lower() == category.lower()]
    return ApiResponse(
        data=[SkillResponse.model_validate(s) for s in skills],
        message=f"Retrieved {len(skills)} skills.",
    )


@router.get(
    "/projects",
    response_model=ApiResponse[List[ProjectResponse]],
    summary="Get Candidate Projects",
    description="Retrieve all portfolio and technical projects extracted from candidate resume.",
)
async def get_profile_projects(
    user_id: uuid.UUID = Depends(get_current_user_id),
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> ApiResponse[List[ProjectResponse]]:
    projects = await project_repo.get_by_user_id(user_id)
    return ApiResponse(
        data=[ProjectResponse.model_validate(p) for p in projects],
        message=f"Retrieved {len(projects)} projects.",
    )


@router.get(
    "/education",
    response_model=ApiResponse[List[EducationResponse]],
    summary="Get Candidate Education",
    description="Retrieve academic credentials and degrees.",
)
async def get_profile_education(
    user_id: uuid.UUID = Depends(get_current_user_id),
    education_repo: EducationRepository = Depends(get_education_repository),
) -> ApiResponse[List[EducationResponse]]:
    education = await education_repo.get_by_user_id(user_id)
    return ApiResponse(
        data=[EducationResponse.model_validate(e) for e in education],
        message=f"Retrieved {len(education)} education entries.",
    )


@router.get(
    "/experience",
    response_model=ApiResponse[List[ExperienceResponse]],
    summary="Get Candidate Experience",
    description="Retrieve work history, roles, and accomplishments.",
)
async def get_profile_experience(
    user_id: uuid.UUID = Depends(get_current_user_id),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
) -> ApiResponse[List[ExperienceResponse]]:
    experience = await experience_repo.get_by_user_id(user_id)
    return ApiResponse(
        data=[ExperienceResponse.model_validate(ex) for ex in experience],
        message=f"Retrieved {len(experience)} experience entries.",
    )


@router.get(
    "/certifications",
    response_model=ApiResponse[List[CertificationResponse]],
    summary="Get Candidate Certifications",
    description="Retrieve professional certifications and issuing authorities.",
)
async def get_profile_certifications(
    user_id: uuid.UUID = Depends(get_current_user_id),
    cert_repo: CertificationRepository = Depends(get_certification_repository),
) -> ApiResponse[List[CertificationResponse]]:
    certifications = await cert_repo.get_by_user_id(user_id)
    return ApiResponse(
        data=[CertificationResponse.model_validate(c) for c in certifications],
        message=f"Retrieved {len(certifications)} certifications.",
    )


@router.get(
    "/full",
    response_model=ApiResponse[ResumeParseResponse],
    summary="Get Complete Candidate Intelligence Profile",
    description="Consolidated profile including contact, summary, skills, projects, education, experience, and certifications.",
)
async def get_full_candidate_intelligence(
    user_id: uuid.UUID = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    skill_repo: SkillRepository = Depends(get_skill_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    education_repo: EducationRepository = Depends(get_education_repository),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
    cert_repo: CertificationRepository = Depends(get_certification_repository),
) -> ApiResponse[ResumeParseResponse]:
    user = await user_repo.get_by_id(user_id)
    profile = await profile_repo.get_by_user_id(user_id)
    skills = await skill_repo.get_by_user_id(user_id)
    projects = await project_repo.get_by_user_id(user_id)
    education = await education_repo.get_by_user_id(user_id)
    experience = await experience_repo.get_by_user_id(user_id)
    certifications = await cert_repo.get_by_user_id(user_id)

    candidate_name = user.name if (user and user.name) else "Candidate"
    candidate_email = user.email if user else ""
    candidate_phone = user.phone if (user and user.phone) else ""
    summary_text = profile.summary if (profile and profile.summary) else ""


    payload = ResumeParseResponse(
        user_id=user_id,
        candidate=CandidateContact(
            name=candidate_name,
            email=candidate_email,
            phone=candidate_phone,
        ),
        summary=summary_text,
        skills=[SkillResponse.model_validate(s) for s in skills],
        projects=[ProjectResponse.model_validate(p) for p in projects],
        education=[EducationResponse.model_validate(e) for e in education],
        experience=[ExperienceResponse.model_validate(ex) for ex in experience],
        certifications=[CertificationResponse.model_validate(c) for c in certifications],
        model_used="gemini-2.5-pro",
    )

    return ApiResponse(
        data=payload,
        message="Full candidate profile intelligence retrieved successfully.",
    )
