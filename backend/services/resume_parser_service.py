"""
Resume Parser Service orchestrating end-to-end resume intelligence.
Extracts raw text, executes multi-attempt AI parsing with fallback,
validates schema, normalizes entities, and persists intelligence models in PostgreSQL.
"""
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession

from core.ai.orchestrator import AIOrchestrator
from core.ai.prompts import RESUME_EXTRACTION_SYSTEM_PROMPT, RESUME_EXTRACTION_USER_PROMPT
from core.exceptions import AIServiceException, NotFoundException, ValidationException
from core.logging import get_logger
from models.certification import CertificationModel
from models.education import EducationModel
from models.experience import ExperienceModel
from models.profile import ProfileModel
from models.project import ProjectModel
from models.skill import SkillModel
from models.user import UserModel
from repositories.candidate_intelligence_repository import (
    CertificationRepository,
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from repositories.user_repository import UserRepository
from schemas.certification import CertificationResponse
from schemas.education import EducationResponse
from schemas.experience import ExperienceResponse
from schemas.project import ProjectResponse
from schemas.resume_analysis import (
    CandidateContact,
    ParsedResumeExtraction,
    ResumeParseResponse,
)
from schemas.skill import SkillResponse
from services.text_extractor import TextExtractor

from core.storage.base import StorageProvider
from core.storage.factory import get_storage_provider

logger = get_logger("services.resume_parser")


class ResumeParserService:
    """
    Production-grade AI Resume Intelligence Service.
    """

    def __init__(
        self,
        session: AsyncSession,
        orchestrator: Optional[AIOrchestrator] = None,
        storage_provider: Optional[StorageProvider] = None,
    ):
        self.session = session
        self.orchestrator = orchestrator or AIOrchestrator()
        self.storage = storage_provider or get_storage_provider()
        self.user_repo = UserRepository(session)

        self.profile_repo = ProfileRepository(session)
        self.resume_repo = ResumeRepository(session)
        self.skill_repo = SkillRepository(session)
        self.project_repo = ProjectRepository(session)
        self.education_repo = EducationRepository(session)
        self.experience_repo = ExperienceRepository(session)
        self.certification_repo = CertificationRepository(session)

    def extract_text(self, file_source: Union[str, Path, bytes], file_type: str) -> str:
        """
        Extracts and normalizes raw text from PDF or DOCX file.
        """
        logger.info(f"Extracting text from resume format: {file_type}")
        return TextExtractor.extract_text(file_source, file_type)

    # Alias matching specification
    def extractText(self, file_source: Union[str, Path, bytes], file_type: str) -> str:
        return self.extract_text(file_source, file_type)

    def validate_response(self, raw_json: str) -> ParsedResumeExtraction:
        """
        Validates the raw LLM completion string against the Pydantic extraction schema.
        """
        try:
            parsed_dict = json.loads(raw_json)
        except Exception as err:
            logger.error("Failed to decode JSON from AI completion", extra={"error": str(err)})
            raise ValidationException(f"AI response is not valid JSON: {str(err)}")

        try:
            return ParsedResumeExtraction.model_validate(parsed_dict)
        except Exception as val_err:
            logger.error("Failed Pydantic schema validation for AI response", extra={"error": str(val_err)})
            raise ValidationException(f"AI output failed schema validation: {str(val_err)}")

    # Alias matching specification
    def validateResponse(self, raw_json: str) -> ParsedResumeExtraction:
        return self.validate_response(raw_json)

    async def save_results(
        self,
        user_id: uuid.UUID,
        data: ParsedResumeExtraction,
        model_used: str,
    ) -> ResumeParseResponse:
        """
        Persists extracted entities atomically and updates candidate profile.
        """
        logger.info(
            f"Persisting candidate intelligence entities for user {user_id}",
            extra={
                "skills_count": len(data.skills),
                "projects_count": len(data.projects),
                "education_count": len(data.education),
                "experience_count": len(data.experience),
                "certifications_count": len(data.certifications),
            },
        )

        # 1. Update User basic info if phone or name extracted and currently blank/default
        user = await self.user_repo.get_by_id(user_id)
        if user:
            if data.phone and (not user.phone or user.phone.strip() == ""):
                user.phone = data.phone
            if data.name and (user.name == "Candidate" or not user.name or user.name.strip() == ""):
                user.name = data.name.strip()
            self.session.add(user)


        # 2. Update Profile summary
        profile = await self.profile_repo.get_by_user_id(user_id)
        summary_text = data.summary or ""
        if profile:
            profile.summary = summary_text
            self.session.add(profile)
        else:
            profile = ProfileModel(user_id=user_id, summary=summary_text)
            self.session.add(profile)

        # 3. Clean existing intelligence records for user (idempotent replacement)
        await self.skill_repo.delete_all_for_user(user_id)
        await self.project_repo.delete_all_for_user(user_id)
        await self.education_repo.delete_all_for_user(user_id)
        await self.experience_repo.delete_all_for_user(user_id)
        await self.certification_repo.delete_all_for_user(user_id)

        # 4. Insert skills
        saved_skills: List[SkillModel] = []
        for s in data.skills:
            skill = SkillModel(
                user_id=user_id,
                name=s.name.strip(),
                category=s.category or "Other",
                confidence_score=s.confidence_score or 0.9,
            )
            self.session.add(skill)
            saved_skills.append(skill)

        # 5. Insert projects
        saved_projects: List[ProjectModel] = []
        for p in data.projects:
            proj = ProjectModel(
                user_id=user_id,
                title=p.title.strip(),
                description=p.description or "",
                technologies=p.technologies or [],
            )
            self.session.add(proj)
            saved_projects.append(proj)

        # 6. Insert education
        saved_education: List[EducationModel] = []
        for edu in data.education:
            ed = EducationModel(
                user_id=user_id,
                institution=edu.institution.strip(),
                degree=edu.degree.strip(),
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
            )
            self.session.add(ed)
            saved_education.append(ed)

        # 7. Insert experience
        saved_experience: List[ExperienceModel] = []
        for exp in data.experience:
            ex = ExperienceModel(
                user_id=user_id,
                company=exp.company.strip(),
                role=exp.role.strip(),
                description=exp.description or "",
                start_date=exp.start_date,
                end_date=exp.end_date,
            )
            self.session.add(ex)
            saved_experience.append(ex)

        # 8. Insert certifications
        saved_certifications: List[CertificationModel] = []
        for cert in data.certifications:
            cr = CertificationModel(
                user_id=user_id,
                name=cert.name.strip(),
                issuer=cert.issuer.strip(),
                issue_date=cert.issue_date,
            )
            self.session.add(cr)
            saved_certifications.append(cr)

        await self.session.commit()


        # Build contact summary
        candidate_name = data.name or (user.name if user else "Candidate")
        candidate_email = data.email or (user.email if user else "")
        candidate_phone = data.phone or (user.phone if user else "")


        return ResumeParseResponse(
            user_id=user_id,
            candidate=CandidateContact(
                name=candidate_name,
                email=candidate_email,
                phone=candidate_phone,
            ),
            summary=summary_text,
            skills=[SkillResponse.model_validate(s) for s in saved_skills],
            projects=[ProjectResponse.model_validate(p) for p in saved_projects],
            education=[EducationResponse.model_validate(e) for e in saved_education],
            experience=[ExperienceResponse.model_validate(ex) for ex in saved_experience],
            certifications=[CertificationResponse.model_validate(c) for c in saved_certifications],
            model_used=model_used,
        )

    # Alias matching specification
    async def saveResults(
        self,
        user_id: uuid.UUID,
        data: ParsedResumeExtraction,
        model_used: str,
    ) -> ResumeParseResponse:
        return await self.save_results(user_id, data, model_used)

    async def parse_resume(
        self,
        user_id: uuid.UUID,
        resume_id: Optional[uuid.UUID] = None,
    ) -> ResumeParseResponse:
        """
        Executes end-to-end resume intelligence pipeline:
        1. Locate active resume file for user
        2. Extract and clean textual content (pypdf / python-docx)
        3. Dispatch to AI orchestrator with primary/fallback retry strategy
        4. Validate AI output against strict Pydantic schema
        5. Normalize and store intelligence records in database
        6. Return complete candidate intelligence profile
        """
        pipeline_start = time.perf_counter()
        logger.info(f"Initiating resume parse pipeline for user {user_id}")

        # 1. Retrieve resume metadata
        if resume_id:
            resume = await self.resume_repo.get_by_id(resume_id)
            if not resume or resume.user_id != user_id:
                raise NotFoundException("Resume record not found.")
        else:
            resume = await self.resume_repo.find_by_user(user_id)
            if not resume:
                raise NotFoundException(
                    "No resume found for this user. Please upload a resume before parsing."
                )

        # Check storage existence
        if not await self.storage.file_exists(resume.file_path):
            logger.error(f"Resume file missing at storage location: {resume.file_path}")
            raise NotFoundException("Resume file not found in storage.")

        file_bytes = await self.storage.get_file(resume.file_path)

        # 2. Extract and clean resume text
        logger.info(f"Extracting text from resume file {resume.original_filename}")
        cleaned_text = self.extract_text(file_bytes, resume.file_type)



        # 3. Format prompt
        user_prompt = RESUME_EXTRACTION_USER_PROMPT.format(resume_text=cleaned_text)

        # 4. Dispatch to multi-attempt AI orchestrator
        logger.info("Executing Gemini AI extraction pipeline with fallback strategy")
        raw_json, telemetry = await self.orchestrator.execute_with_fallback(
            prompt=user_prompt,
            system_instruction=RESUME_EXTRACTION_SYSTEM_PROMPT,
        )

        # 5. Validate AI response
        validated_data = self.validate_response(raw_json)

        # 6. Save results to database
        model_used = telemetry.get("model_used", "gemini-2.5-pro")
        parse_response = await self.save_results(
            user_id=user_id,
            data=validated_data,
            model_used=model_used,
        )

        total_time_ms = round((time.perf_counter() - pipeline_start) * 1000, 2)
        logger.info(
            f"Resume parse completed successfully for user {user_id} in {total_time_ms}ms",
            extra={"total_time_ms": total_time_ms, "model_used": model_used},
        )

        return parse_response

    # Alias matching specification
    async def parseResume(
        self,
        user_id: uuid.UUID,
        resume_id: Optional[uuid.UUID] = None,
    ) -> ResumeParseResponse:
        return await self.parse_resume(user_id, resume_id)
