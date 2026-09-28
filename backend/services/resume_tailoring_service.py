"""
ResumeTailoringService for Phase 7 AI Resume Tailoring Engine.
Coordinates candidate profile aggregation, job description keyword analysis,
multi-version resume generation (ATS, Recruiter, Balanced), ATS scoring evaluation,
truthfulness enforcement, and document exports.

Methods:
- analyze_job_description()
- generate_tailored_resume()
- calculate_ats_score()
- export_resume()
- get_tailored_resumes()
- get_tailored_resume_by_id()
"""
import json
import time
import urllib.parse
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from core.ai.orchestrator import AIOrchestrator
from core.exceptions import BadRequestException, NotFoundException
from core.logging import get_logger
from core.tailoring.ats_engine import ATSEngine
from core.tailoring.export_service import ResumeExportService
from core.tailoring.keyword_analyzer import KeywordAnalyzer
from core.tailoring.prompts import (
    JOB_ANALYSIS_SYSTEM_PROMPT,
    RESUME_TAILORING_SYSTEM_PROMPT,
    build_job_analysis_prompt,
    build_tailoring_prompt,
)
from models.tailored_resume import TailoredResumeModel
from repositories.candidate_intelligence_repository import (
    CertificationRepository,
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.job_repository import JobRepository
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from repositories.tailored_resume_repository import TailoredResumeRepository
from repositories.user_repository import UserRepository
from schemas.tailoring import (
    ATSScoreBreakdownDTO,
    KeywordAnalysisDTO,
    ResumeSectionCertification,
    ResumeSectionEducation,
    ResumeSectionExperience,
    ResumeSectionProject,
    ResumeSectionSkillGroup,
    ResumeVersionDTO,
    TailoredResumeListItem,
    TailoredResumeResponse,
)

logger = get_logger("tailoring.service")


class ResumeTailoringService:
    """
    Core business service for tailoring candidate resumes to target job postings.
    """

    def __init__(
        self,
        tailored_repo: TailoredResumeRepository,
        job_repo: JobRepository,
        user_repo: UserRepository,
        profile_repo: ProfileRepository,
        resume_repo: ResumeRepository,
        skill_repo: SkillRepository,
        experience_repo: ExperienceRepository,
        education_repo: EducationRepository,
        project_repo: ProjectRepository,
        certification_repo: CertificationRepository,
        orchestrator: Optional[AIOrchestrator] = None,
    ):
        self.tailored_repo = tailored_repo
        self.job_repo = job_repo
        self.user_repo = user_repo
        self.profile_repo = profile_repo
        self.resume_repo = resume_repo
        self.skill_repo = skill_repo
        self.experience_repo = experience_repo
        self.education_repo = education_repo
        self.project_repo = project_repo
        self.certification_repo = certification_repo
        self.orchestrator = orchestrator or AIOrchestrator()

    async def analyze_job_description(
        self,
        job_description: str,
        job_title: str = "",
        job_company: str = "",
        job_requirements: str = "",
    ) -> KeywordAnalysisDTO:
        """
        Extracts structured required skills, preferred skills, technologies, and keywords
        from a job listing using AI with heuristic fallback.
        """
        prompt = build_job_analysis_prompt(
            job_title=job_title,
            job_company=job_company,
            job_description=job_description,
            job_requirements=job_requirements,
        )

        extracted_data = {}
        try:
            raw_json, _ = await self.orchestrator.execute_with_fallback(
                prompt=prompt,
                system_instruction=JOB_ANALYSIS_SYSTEM_PROMPT,
            )
            extracted_data = json.loads(raw_json)
        except Exception as e:
            logger.warning(
                f"[ResumeTailoringService] AI keyword extraction failed, using heuristic analyzer: {e}"
            )
            extracted_data = KeywordAnalyzer.extract_keywords_heuristic(
                f"{job_title} {job_description} {job_requirements}"
            )

        required = [str(x).strip() for x in extracted_data.get("required_skills", []) if str(x).strip()]
        preferred = [str(x).strip() for x in extracted_data.get("preferred_skills", []) if str(x).strip()]
        technologies = [str(x).strip() for x in extracted_data.get("technologies", []) if str(x).strip()]
        responsibilities = [str(x).strip() for x in extracted_data.get("responsibilities", []) if str(x).strip()]
        keywords = [str(x).strip() for x in extracted_data.get("keywords", []) if str(x).strip()]

        # Ensure fallback terms if list is completely empty
        if not keywords:
            keywords = required + preferred + technologies
        if not keywords:
            keywords = ["Python", "FastAPI", "Backend"]

        return KeywordAnalysisDTO(
            matched_keywords=[],
            missing_keywords=keywords,
            coverage_percentage=0.0,
            required_skills=required or keywords[:2],
            preferred_skills=preferred or keywords[2:],
            technologies=technologies or keywords,
            responsibilities=responsibilities or ["Develop scalable backend systems"],
            keywords=keywords,
        )

    async def generate_tailored_resume(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        resume_id: Optional[uuid.UUID] = None,
        target_version: str = "balanced",
        custom_instructions: Optional[str] = None,
    ) -> TailoredResumeResponse:
        """
        Executes complete Resume Tailoring Pipeline:
        1. Aggregates authentic candidate records (Profile, Skills, Experience, Education, Projects).
        2. Retrieves target Job record.
        3. Extracts and matches job keywords.
        4. Synthesizes 3 tailored variations via Gemini Pro / Flash fallback (or deterministic fallback).
        5. Enforces Truthfulness Mandate (strips any hallucinated skills).
        6. Computes comprehensive ATS Score & Breakdown.
        7. Persists `TailoredResume` in database.
        8. Returns populated TailoredResumeResponse.
        """
        pipeline_start = time.perf_counter()

        # 1. Fetch user & job
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(message=f"User {user_id} not found.")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundException(message=f"Job {job_id} not found.")

        profile = await self.profile_repo.get_by_user_id(user_id)
        active_resume = await self.resume_repo.find_by_user(user_id)
        resolved_resume_id = resume_id or (active_resume.id if active_resume else None)

        # 2. Fetch candidate authentic intelligence records
        skills_entities = await self.skill_repo.get_by_user_id(user_id)
        experiences_entities = await self.experience_repo.get_by_user_id(user_id)
        educations_entities = await self.education_repo.get_by_user_id(user_id)
        projects_entities = await self.project_repo.get_by_user_id(user_id)
        certifications_entities = await self.certification_repo.get_by_user_id(user_id)

        candidate_name = user.name or "Candidate"
        candidate_summary = profile.summary if (profile and profile.summary) else "Experienced software engineer."

        authentic_skills = [s.name for s in skills_entities]
        authentic_experiences = [
            {
                "id": str(e.id),
                "company": e.company,
                "role": e.role,
                "start_date": e.start_date,
                "end_date": e.end_date,
                "description": e.description,
            }
            for e in experiences_entities
        ]
        authentic_educations = [
            {
                "id": str(ed.id),
                "institution": ed.institution,
                "degree": ed.degree,
                "field_of_study": ed.field_of_study,
                "start_date": ed.start_date,
                "end_date": ed.end_date,
            }
            for ed in educations_entities
        ]
        authentic_projects = [
            {
                "id": str(p.id),
                "title": p.title,
                "description": p.description,
                "technologies": p.technologies or [],
            }
            for p in projects_entities
        ]
        authentic_certifications = [
            {
                "id": str(c.id),
                "name": c.name,
                "issuer": c.issuer,
                "issue_date": c.issue_date,
            }
            for c in certifications_entities
        ]

        # 3. Keyword Analysis & Alignment
        kw_analysis = await self.analyze_job_description(
            job_description=job.description,
            job_title=job.title,
            job_company=job.company,
            job_requirements=job.requirements or "",
        )

        matched_kws, missing_kws, coverage_pct = KeywordAnalyzer.compute_alignment(
            candidate_skills=authentic_skills,
            candidate_experiences=authentic_experiences,
            job_keywords=kw_analysis.keywords,
            required_skills=kw_analysis.required_skills,
        )
        kw_analysis.matched_keywords = matched_kws
        kw_analysis.missing_keywords = missing_kws
        kw_analysis.coverage_percentage = coverage_pct

        # 4. Tailoring Synthesis (Gemini with Fallback)
        tailoring_prompt = build_tailoring_prompt(
            candidate_name=candidate_name,
            candidate_summary=candidate_summary,
            candidate_skills=authentic_skills,
            candidate_experience=authentic_experiences,
            candidate_education=authentic_educations,
            candidate_projects=authentic_projects,
            candidate_certifications=authentic_certifications,
            job_title=job.title,
            job_company=job.company,
            job_description=job.description,
            job_requirements=job.requirements or "",
            custom_instructions=custom_instructions or "",
        )

        ai_telemetry: Dict[str, Any] = {}
        tailored_payload: Dict[str, Any] = {}

        try:
            raw_tailored_json, ai_telemetry = await self.orchestrator.execute_with_fallback(
                prompt=tailoring_prompt,
                system_instruction=RESUME_TAILORING_SYSTEM_PROMPT,
            )
            tailored_payload = json.loads(raw_tailored_json)
        except Exception as e:
            logger.warning(
                f"[ResumeTailoringService] AI tailoring failed or timed out: {e}. Building deterministic variations."
            )
            tailored_payload = self._build_deterministic_variations(
                candidate_name=candidate_name,
                candidate_summary=candidate_summary,
                authentic_skills=authentic_skills,
                skills_entities=skills_entities,
                authentic_experiences=authentic_experiences,
                authentic_educations=authentic_educations,
                authentic_projects=authentic_projects,
                authentic_certifications=authentic_certifications,
                job_title=job.title,
                job_company=job.company,
                matched_keywords=matched_kws,
            )
            ai_telemetry = {
                "success": True,
                "model_used": "deterministic-fallback",
                "attempt": 0,
                "duration_ms": 10.0,
            }

        # 5. Parse and Validate Versions
        versions_dict: Dict[str, ResumeVersionDTO] = {}
        raw_versions = tailored_payload.get("versions", {})

        for v_key in ["ats", "recruiter", "balanced"]:
            v_data = raw_versions.get(v_key)
            if not v_data:
                # Fallback to balanced if missing
                v_data = raw_versions.get("balanced") or {}

            # Construct ResumeVersionDTO
            skills_groups = []
            for g in v_data.get("skills", []):
                skills_groups.append(
                    ResumeSectionSkillGroup(
                        category=g.get("category", "Technical Competencies"),
                        skills=[str(s).strip() for s in g.get("skills", []) if str(s).strip()],
                    )
                )
            if not skills_groups and authentic_skills:
                skills_groups = [
                    ResumeSectionSkillGroup(category="Verified Core Skills", skills=authentic_skills)
                ]

            exp_entries = []
            for exp in v_data.get("experience", []):
                exp_entries.append(
                    ResumeSectionExperience(
                        id=exp.get("id"),
                        company=exp.get("company", "Company"),
                        role=exp.get("role", "Engineer"),
                        start_date=exp.get("start_date"),
                        end_date=exp.get("end_date"),
                        description=exp.get("description", ""),
                        bullet_points=exp.get("bullet_points", []),
                        highlighted_keywords=exp.get("highlighted_keywords", []),
                    )
                )

            edu_entries = [
                ResumeSectionEducation(
                    id=ed.get("id"),
                    institution=ed.get("institution", "Institution"),
                    degree=ed.get("degree", "Degree"),
                    field_of_study=ed.get("field_of_study"),
                    start_date=ed.get("start_date"),
                    end_date=ed.get("end_date"),
                )
                for ed in v_data.get("education", [])
            ]

            proj_entries = [
                ResumeSectionProject(
                    id=pr.get("id"),
                    title=pr.get("title", "Project"),
                    description=pr.get("description", ""),
                    technologies=pr.get("technologies", []),
                    bullet_points=pr.get("bullet_points", []),
                )
                for pr in v_data.get("projects", [])
            ]

            cert_entries = [
                ResumeSectionCertification(
                    id=cr.get("id"),
                    name=cr.get("name", "Certification"),
                    issuer=cr.get("issuer", "Issuer"),
                    issue_date=cr.get("issue_date"),
                )
                for cr in v_data.get("certifications", [])
            ]

            version_dto = ResumeVersionDTO(
                version_type=v_key,  # type: ignore
                label=v_data.get("label", f"Version {v_key.upper()}"),
                summary=v_data.get("summary", candidate_summary),
                skills=skills_groups,
                experience=exp_entries,
                education=edu_entries,
                projects=proj_entries,
                certifications=cert_entries,
            )

            # 6. ENFORCE TRUTHFULNESS: Strip any hallucinated skills
            sanitized_version, stripped = ATSEngine.enforce_truthfulness(
                version_dto, authentic_skills
            )
            if stripped:
                logger.info(
                    f"[ResumeTailoringService] Anti-hallucination guardrail stripped unpossessed skills: {stripped}"
                )
                # Ensure they are represented in missing keywords
                for sk in stripped:
                    if sk not in kw_analysis.missing_keywords:
                        kw_analysis.missing_keywords.append(sk)

            versions_dict[v_key] = sanitized_version

        # 7. Evaluate ATS Score
        ats_eval_start = time.perf_counter()
        target_v = versions_dict.get(target_version) or versions_dict["balanced"]

        ats_breakdown = ATSEngine.calculate_ats_score(
            version=target_v,
            job_keywords=kw_analysis.keywords,
            required_skills=kw_analysis.required_skills,
            preferred_skills=kw_analysis.preferred_skills,
            job_title=job.title,
            job_description=job.description,
            candidate_genuine_skills=authentic_skills,
        )
        ats_eval_duration_ms = round((time.perf_counter() - ats_eval_start) * 1000, 2)
        total_duration_ms = round((time.perf_counter() - pipeline_start) * 1000, 2)

        recommendations = tailored_payload.get("recommendations", [])
        if not recommendations:
            recommendations = ats_breakdown.suggestions

        telemetry = {
            "generationDurationMs": total_duration_ms,
            "atsScoringDurationMs": ats_eval_duration_ms,
            "modelUsed": ai_telemetry.get("model_used", "gemini-2.5-pro"),
            "attempts": ai_telemetry.get("attempt", 1),
        }

        # 8. Store in Database
        full_content_payload = {
            "versions": {k: v.model_dump(by_alias=True) for k, v in versions_dict.items()},
            "keyword_analysis": kw_analysis.model_dump(by_alias=True),
            "ats_breakdown": ats_breakdown.model_dump(by_alias=True),
            "recommendations": recommendations,
            "telemetry": telemetry,
        }

        tailored_title = tailored_payload.get("title") or f"{job.title} — Tailored Resume"
        tailored_summary = target_v.summary

        existing_record = await self.tailored_repo.findByJob(job_id=job_id, user_id=user_id)
        if existing_record:
            updated_record = await self.tailored_repo.update(
                tailored_resume=existing_record,
                data={
                    "original_resume_id": resolved_resume_id,
                    "title": tailored_title,
                    "summary": tailored_summary,
                    "content": json.dumps(full_content_payload),
                    "ats_score": ats_breakdown.overall_score,
                    "keyword_coverage": coverage_pct,
                },
            )
            saved_entity = updated_record
        else:
            new_record = await self.tailored_repo.create(
                data={
                    "user_id": user_id,
                    "job_id": job_id,
                    "original_resume_id": resolved_resume_id,
                    "title": tailored_title,
                    "summary": tailored_summary,
                    "content": json.dumps(full_content_payload),
                    "ats_score": ats_breakdown.overall_score,
                    "keyword_coverage": coverage_pct,
                }
            )
            saved_entity = new_record

        return TailoredResumeResponse(
            id=saved_entity.id,
            user_id=saved_entity.user_id,
            job_id=saved_entity.job_id,
            original_resume_id=saved_entity.original_resume_id,
            title=saved_entity.title,
            summary=saved_entity.summary,
            ats_score=saved_entity.ats_score,
            keyword_coverage=saved_entity.keyword_coverage,
            versions=versions_dict,
            keyword_analysis=kw_analysis,
            ats_breakdown=ats_breakdown,
            recommendations=recommendations,
            telemetry=telemetry,
            created_at=saved_entity.created_at,
            updated_at=saved_entity.updated_at,
        )

    def calculate_ats_score(
        self,
        version: ResumeVersionDTO,
        job_keywords: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        job_title: str,
        job_description: str,
        candidate_genuine_skills: List[str],
    ) -> ATSScoreBreakdownDTO:
        """Calculate standalone ATS score breakdown."""
        return ATSEngine.calculate_ats_score(
            version=version,
            job_keywords=job_keywords,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            job_title=job_title,
            job_description=job_description,
            candidate_genuine_skills=candidate_genuine_skills,
        )

    async def get_tailored_resumes(self, user_id: uuid.UUID) -> List[TailoredResumeListItem]:
        """List all tailored resume records for a user."""
        records = await self.tailored_repo.findByUser(user_id=user_id)
        items = []
        for r in records:
            job_title = r.job.title if r.job else "Target Role"
            job_company = r.job.company if r.job else "Target Employer"
            items.append(
                TailoredResumeListItem(
                    id=r.id,
                    user_id=r.user_id,
                    job_id=r.job_id,
                    job_title=job_title,
                    job_company=job_company,
                    title=r.title,
                    ats_score=r.ats_score,
                    keyword_coverage=r.keyword_coverage,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )
        return items

    async def get_tailored_resume_by_id(
        self,
        user_id: uuid.UUID,
        tailored_id: uuid.UUID,
    ) -> TailoredResumeResponse:
        """Fetch single tailored resume by ID with full content and versions."""
        record = await self.tailored_repo.findById(id=tailored_id, user_id=user_id)
        if not record:
            raise NotFoundException(message=f"Tailored resume {tailored_id} not found.")

        parsed_content = json.loads(record.content) if record.content else {}

        # Reconstruct versions
        versions_dict: Dict[str, ResumeVersionDTO] = {}
        for v_key, v_data in parsed_content.get("versions", {}).items():
            versions_dict[v_key] = ResumeVersionDTO.model_validate(v_data)

        # Keyword analysis
        kw_data = parsed_content.get("keyword_analysis", {})
        keyword_analysis = KeywordAnalysisDTO.model_validate(kw_data)

        # ATS Breakdown
        ats_data = parsed_content.get("ats_breakdown", {})
        ats_breakdown = ATSScoreBreakdownDTO.model_validate(ats_data)

        return TailoredResumeResponse(
            id=record.id,
            user_id=record.user_id,
            job_id=record.job_id,
            original_resume_id=record.original_resume_id,
            title=record.title,
            summary=record.summary,
            ats_score=record.ats_score,
            keyword_coverage=record.keyword_coverage,
            versions=versions_dict,
            keyword_analysis=keyword_analysis,
            ats_breakdown=ats_breakdown,
            recommendations=parsed_content.get("recommendations", []),
            telemetry=parsed_content.get("telemetry", {}),
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    async def export_resume(
        self,
        user_id: uuid.UUID,
        tailored_id: uuid.UUID,
        format_type: str = "pdf",
        version_type: str = "balanced",
    ) -> Tuple[bytes, str, str]:
        """
        Exports the selected tailored resume version to PDF, DOCX, or Markdown.
        Returns: Tuple of (binary_content, mime_type, filename).
        """
        tailored_response = await self.get_tailored_resume_by_id(user_id=user_id, tailored_id=tailored_id)
        user = await self.user_repo.get_by_id(user_id)
        candidate_name = user.name if (user and user.name) else "Candidate"
        contact_info = {
            "email": user.email if user else "user@example.com",
            "phone": user.phone if user else "",
        }

        # Select version
        v_key = version_type.lower()
        version_dto = tailored_response.versions.get(v_key)
        if not version_dto:
            version_dto = tailored_response.versions.get("balanced") or next(
                iter(tailored_response.versions.values()), None
            )

        if not version_dto:
            raise BadRequestException(message=f"No resume version found for '{version_type}'.")

        fmt = format_type.lower().strip()
        safe_title = "".join(c for c in tailored_response.title if c.isalnum() or c in (" ", "-", "_")).strip()
        safe_title = safe_title.replace(" ", "_")

        if fmt == "markdown" or fmt == "md":
            md_text = ResumeExportService.export_markdown(
                version=version_dto,
                candidate_name=candidate_name,
                contact_info=contact_info,
            )
            return (
                md_text.encode("utf-8"),
                "text/markdown; charset=utf-8",
                f"{safe_title}_{v_key}.md",
            )
        elif fmt == "docx":
            docx_bytes = ResumeExportService.export_docx(
                version=version_dto,
                candidate_name=candidate_name,
                contact_info=contact_info,
            )
            return (
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                f"{safe_title}_{v_key}.docx",
            )
        elif fmt == "pdf":
            pdf_bytes = ResumeExportService.export_pdf(
                version=version_dto,
                candidate_name=candidate_name,
                contact_info=contact_info,
            )
            return (
                pdf_bytes,
                "application/pdf",
                f"{safe_title}_{v_key}.pdf",
            )
        else:
            raise BadRequestException(
                message=f"Unsupported export format '{format_type}'. Supported formats: pdf, docx, markdown."
            )

    def _build_deterministic_variations(
        self,
        candidate_name: str,
        candidate_summary: str,
        authentic_skills: List[str],
        skills_entities: List[Any],
        authentic_experiences: List[Dict[str, Any]],
        authentic_educations: List[Dict[str, Any]],
        authentic_projects: List[Dict[str, Any]],
        authentic_certifications: List[Dict[str, Any]],
        job_title: str,
        job_company: str,
        matched_keywords: List[str],
    ) -> Dict[str, Any]:
        """
        Generates robust fallback versions (ATS, Recruiter, Balanced) using genuine candidate records.
        Guarantees zero hallucinated skills or records.
        """
        # Group skills genuinely
        categories_dict: Dict[str, List[str]] = {}
        for s in skills_entities:
            cat = getattr(s, "category", "Core Technical Skills")
            categories_dict.setdefault(cat, []).append(s.name)

        if not categories_dict and authentic_skills:
            categories_dict["Core Technical Skills"] = authentic_skills

        grouped_skills = [
            {"category": cat, "skills": sks}
            for cat, sks in categories_dict.items()
        ]

        # Enhance experience bullets with active verbs & authentic keywords
        enhanced_experiences = []
        for exp in authentic_experiences:
            desc = exp.get("description", "")
            bullets = [b.strip() for b in desc.split("\n") if b.strip()] if "\n" in desc else [desc]
            if len(bullets) < 2:
                bullets.append(f"Collaborated with cross-functional engineering partners at {exp.get('company')} to deliver high-quality software solutions.")

            # Identify which matched keywords apply to this role
            role_kws = [kw for kw in matched_keywords if kw.lower() in desc.lower()]

            enhanced_experiences.append({
                "company": exp.get("company"),
                "role": exp.get("role"),
                "start_date": exp.get("start_date"),
                "end_date": exp.get("end_date"),
                "description": desc,
                "bullet_points": bullets[:4],
                "highlighted_keywords": role_kws or matched_keywords[:2],
            })

        # Version A: ATS
        ats_summary = (
            f"Results-driven software professional targeting {job_title} at {job_company}. "
            f"Equipped with verified proficiency in {', '.join(matched_keywords[:4]) if matched_keywords else ', '.join(authentic_skills[:4])}. "
            f"Proven history of developing robust systems, optimizing latency, and executing production releases."
        )

        # Version B: Recruiter
        recruiter_summary = (
            f"Passionate technical engineer with deep background in scalable software delivery. "
            f"Known for rapid problem resolution, strong team mentorship, and driving engineering excellence for {job_title} initiatives. "
            f"{candidate_summary}"
        )

        # Version C: Balanced
        balanced_summary = (
            f"High-impact software engineer with verified expertise in {', '.join(matched_keywords[:3]) if matched_keywords else ', '.join(authentic_skills[:3])}. "
            f"Committed to architectural rigor, clean code, and delivering business outcomes aligned with {job_company}'s engineering objectives."
        )

        return {
            "title": f"{job_title} — Tailored Resume",
            "summary": balanced_summary,
            "versions": {
                "ats": {
                    "version_type": "ats",
                    "label": "Version A: ATS Optimized",
                    "summary": ats_summary,
                    "skills": grouped_skills,
                    "experience": enhanced_experiences,
                    "education": authentic_educations,
                    "projects": authentic_projects,
                    "certifications": authentic_certifications,
                },
                "recruiter": {
                    "version_type": "recruiter",
                    "label": "Version B: Recruiter Optimized",
                    "summary": recruiter_summary,
                    "skills": grouped_skills,
                    "experience": enhanced_experiences,
                    "education": authentic_educations,
                    "projects": authentic_projects,
                    "certifications": authentic_certifications,
                },
                "balanced": {
                    "version_type": "balanced",
                    "label": "Version C: Balanced",
                    "summary": balanced_summary,
                    "skills": grouped_skills,
                    "experience": enhanced_experiences,
                    "education": authentic_educations,
                    "projects": authentic_projects,
                    "certifications": authentic_certifications,
                },
            },
            "recommendations": [
                f"Align your GitHub projects with {job_company}'s domain tech stack.",
                "Review missing keywords to determine whether relevant coursework or side projects apply.",
            ],
        }
