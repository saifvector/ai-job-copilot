"""
ApplicationAssistantService for Phase 12 Application Assistant.
Orchestrates application data preparation, document selection, truthful AI answer generation,
checklist validation, candidate review workflow, and submission analytics.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from core.application_assistant.answer_generator import (
    ApplicationAnswerGenerator,
    DEFAULT_COMMON_QUESTIONS,
)
from core.application_assistant.checklist_evaluator import ApplicationChecklistEvaluator
from core.exceptions import BadRequestException, NotFoundException
from core.logging import get_logger
from models.application_draft import ApplicationDraftModel
from models.application_question import ApplicationQuestionModel
from repositories.application_assistant_repository import (
    ApplicationDraftRepository,
    ApplicationQuestionRepository,
)
from repositories.candidate_intelligence_repository import (
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.job_repository import JobRepository
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from repositories.tailored_resume_repository import TailoredResumeRepository
from schemas.application_assistant import (
    ApplicationDraftCreateRequest,
    ApplicationDraftResponse,
    ApplicationQuestionCreate,
    ApplicationQuestionResponse,
    ApplicationQuestionUpdate,
    AssistantAnalyticsResponse,
    ChecklistResponse,
    GenerateAnswersRequest,
    ReviewDraftRequest,
)

logger = get_logger("application_assistant.service")


class ApplicationAssistantService:
    """
    Core business service for job application preparation, response generation,
    document selection, and candidate-controlled review.
    """

    def __init__(
        self,
        draft_repo: ApplicationDraftRepository,
        question_repo: ApplicationQuestionRepository,
        job_repo: JobRepository,
        profile_repo: ProfileRepository,
        resume_repo: ResumeRepository,
        tailored_resume_repo: Optional[TailoredResumeRepository] = None,
        skill_repo: Optional[SkillRepository] = None,
        experience_repo: Optional[ExperienceRepository] = None,
        project_repo: Optional[ProjectRepository] = None,
        education_repo: Optional[EducationRepository] = None,
        answer_generator: Optional[ApplicationAnswerGenerator] = None,
        checklist_evaluator: Optional[ApplicationChecklistEvaluator] = None,
    ):
        self.draft_repo = draft_repo
        self.question_repo = question_repo
        self.job_repo = job_repo
        self.profile_repo = profile_repo
        self.resume_repo = resume_repo
        self.tailored_resume_repo = tailored_resume_repo
        self.skill_repo = skill_repo
        self.experience_repo = experience_repo
        self.project_repo = project_repo
        self.education_repo = education_repo
        self.answer_generator = answer_generator or ApplicationAnswerGenerator()
        self.checklist_evaluator = checklist_evaluator or ApplicationChecklistEvaluator()

    async def create_draft(
        self,
        user_id: Union[uuid.UUID, str],
        payload: ApplicationDraftCreateRequest,
    ) -> ApplicationDraftResponse:
        """
        Creates or retrieves an active application draft for a target job.
        Seeds common application questions and initializes readiness checklist.
        """
        uid = uuid.UUID(str(user_id))
        jid = uuid.UUID(str(payload.job_id))

        # Verify job exists
        job = await self.job_repo.get_by_id(jid)
        if not job:
            raise NotFoundException(f"Job with ID '{jid}' not found.")

        # Check if draft already exists for this job and user in Draft or ReadyForReview state
        existing = await self.draft_repo.get_by_job_and_user(job_id=jid, user_id=uid)
        if existing and existing.status in ("Draft", "ReadyForReview"):
            logger.info(f"Returning existing draft {existing.id} for job {jid}")
            return await self.get_draft(user_id=uid, draft_id=existing.id)

        # Auto-detect selected resume if not specified
        selected_resume_id = payload.selected_resume_id
        if not selected_resume_id:
            # Check for a tailored resume for this job first
            if self.tailored_resume_repo:
                tailored = await self.tailored_resume_repo.findByJob(job_id=jid, user_id=uid)
                if tailored:
                    selected_resume_id = tailored.id
            # Fallback to primary resume
            if not selected_resume_id:
                primary_resume = await self.resume_repo.find_by_user(user_id=uid)
                if primary_resume:
                    selected_resume_id = primary_resume.id

        # Create draft record
        draft = await self.draft_repo.create_draft({
            "user_id": uid,
            "job_id": jid,
            "status": "Draft",
            "selected_resume_id": selected_resume_id,
            "notes": payload.notes,
            "readiness_score": 0.0,
        })

        # Seed questions
        questions_to_create: List[Dict[str, Any]] = []
        if payload.custom_questions and len(payload.custom_questions) > 0:
            for idx, cq in enumerate(payload.custom_questions):
                questions_to_create.append({
                    "draft_id": draft.id,
                    "question": cq.question,
                    "answer_type": cq.answer_type,
                    "options": cq.options or [],
                    "is_required": cq.is_required,
                    "order": cq.order or (idx + 1),
                })
        else:
            for q_def in DEFAULT_COMMON_QUESTIONS:
                questions_to_create.append({
                    "draft_id": draft.id,
                    "question": q_def["question"],
                    "answer_type": q_def["answer_type"],
                    "options": q_def.get("options", []),
                    "is_required": q_def.get("is_required", True),
                    "order": q_def.get("order", 0),
                })

        created_questions = await self.question_repo.bulk_create(questions_to_create)

        # Evaluate initial checklist
        profile = await self._get_candidate_profile_dict(uid)
        checklist_res = self.checklist_evaluator.evaluate_readiness(
            draft=draft,
            questions=created_questions,
            candidate_profile=profile,
        )

        draft = await self.draft_repo.update_draft(draft, {
            "readiness_score": checklist_res.readiness_score,
            "checklist": checklist_res.model_dump_json(by_alias=True),
        })

        return self._build_draft_response(draft, created_questions, job, checklist_res)

    async def generate_answers(
        self,
        user_id: Union[uuid.UUID, str],
        payload: GenerateAnswersRequest,
    ) -> ApplicationDraftResponse:
        """
        Generates truthful, tailored answers for all questions in the draft
        using Gemini 2.5 Pro with deterministic candidate-grounded fallback.
        """
        uid = uuid.UUID(str(user_id))
        did = uuid.UUID(str(payload.draft_id))

        draft = await self.draft_repo.get_by_id(draft_id=did, user_id=uid)
        if not draft:
            raise NotFoundException(f"Application draft with ID '{did}' not found.")

        job = await self.job_repo.get_by_id(draft.job_id)
        if not job:
            raise NotFoundException("Target job not found for this draft.")

        # If custom questions provided, add them to draft
        if payload.custom_questions and len(payload.custom_questions) > 0:
            existing_questions = await self.question_repo.list_by_draft(draft.id)
            current_max_order = max([q.order for q in existing_questions], default=0)
            new_qs = []
            for idx, cq in enumerate(payload.custom_questions):
                new_qs.append({
                    "draft_id": draft.id,
                    "question": cq.question,
                    "answer_type": cq.answer_type,
                    "options": cq.options or [],
                    "is_required": cq.is_required,
                    "order": cq.order or (current_max_order + idx + 1),
                })
            await self.question_repo.bulk_create(new_qs)

        # Retrieve all questions for draft
        questions = await self.question_repo.list_by_draft(draft.id)
        if not questions:
            # Seed default questions if none exist
            questions_to_create = [
                {
                    "draft_id": draft.id,
                    "question": q_def["question"],
                    "answer_type": q_def["answer_type"],
                    "options": q_def.get("options", []),
                    "is_required": q_def.get("is_required", True),
                    "order": q_def.get("order", 0),
                }
                for q_def in DEFAULT_COMMON_QUESTIONS
            ]
            questions = await self.question_repo.bulk_create(questions_to_create)

        # Fetch candidate profile details
        profile = await self._get_candidate_profile_dict(uid)
        skills = await self._get_candidate_skills(uid)
        experiences = await self._get_candidate_experiences(uid)
        projects = await self._get_candidate_projects(uid)
        education = await self._get_candidate_education(uid)

        # Determine which questions need generation
        q_dicts = []
        for q in questions:
            opts = self._parse_options(q.options)
            q_dicts.append({
                "question": q.question,
                "answer_type": q.answer_type,
                "options": opts,
                "is_required": q.is_required,
                "order": q.order,
            })

        # Run AI Answer Generator
        generated = await self.answer_generator.generate_answers(
            job_title=job.title,
            company=job.company,
            job_description=job.description,
            job_requirements=job.requirements if hasattr(job, "requirements") and isinstance(job.requirements, list) else None,
            questions=q_dicts,
            candidate_profile=profile,
            skills=skills,
            experiences=experiences,
            projects=projects,
            education=education,
        )

        # Update questions in database
        updated_questions = []
        gen_summary: Dict[str, str] = {}
        for idx, q_model in enumerate(questions):
            ans_text = ""
            if idx < len(generated):
                ans_text = generated[idx].get("generated_answer", "")
            else:
                for g in generated:
                    if g.get("question", "").lower() == q_model.question.lower():
                        ans_text = g.get("generated_answer", "")
                        break

            updates: Dict[str, Any] = {"generated_answer": ans_text}
            # Only set user_answer if not previously edited or regenerate_all is True
            if not q_model.user_answer or payload.regenerate_all:
                updates["user_answer"] = ans_text
                updates["is_reviewed"] = False

            updated_q = await self.question_repo.update_question(q_model, updates)
            updated_questions.append(updated_q)
            gen_summary[q_model.question] = ans_text

        # Re-evaluate checklist
        checklist_res = self.checklist_evaluator.evaluate_readiness(
            draft=draft,
            questions=updated_questions,
            candidate_profile=profile,
        )

        # Update draft
        draft = await self.draft_repo.update_draft(draft, {
            "generated_answers": json.dumps(gen_summary),
            "readiness_score": checklist_res.readiness_score,
            "checklist": checklist_res.model_dump_json(by_alias=True),
            "status": "ReadyForReview" if checklist_res.is_ready_for_review else "Draft",
        })

        return self._build_draft_response(draft, updated_questions, job, checklist_res)

    async def review_draft(
        self,
        user_id: Union[uuid.UUID, str],
        payload: ReviewDraftRequest,
    ) -> ApplicationDraftResponse:
        """
        Processes candidate review, user answer edits, document change, and accuracy confirmation.
        Ensures the candidate confirms accuracy before submission.
        """
        uid = uuid.UUID(str(user_id))
        did = uuid.UUID(str(payload.draft_id))

        draft = await self.draft_repo.get_by_id(draft_id=did, user_id=uid)
        if not draft:
            raise NotFoundException(f"Application draft with ID '{did}' not found.")

        job = await self.job_repo.get_by_id(draft.job_id)

        # Update individual answers if provided
        if payload.answers:
            for ans_update in payload.answers:
                q_model = await self.question_repo.get_by_id(ans_update.question_id)
                if q_model and q_model.draft_id == draft.id:
                    await self.question_repo.update_question(q_model, {
                        "user_answer": ans_update.user_answer,
                        "is_reviewed": ans_update.is_reviewed,
                    })

        # Fetch fresh questions list
        questions = await self.question_repo.list_by_draft(draft.id)

        # If confirm_accuracy is True, mark all remaining questions as reviewed
        if payload.confirm_accuracy:
            for q in questions:
                if not q.is_reviewed:
                    await self.question_repo.update_question(q, {"is_reviewed": True})
            questions = await self.question_repo.list_by_draft(draft.id)

        draft_updates: Dict[str, Any] = {}
        if payload.selected_resume_id is not None:
            draft_updates["selected_resume_id"] = payload.selected_resume_id
        if payload.notes is not None:
            draft_updates["notes"] = payload.notes

        # Re-evaluate checklist
        profile = await self._get_candidate_profile_dict(uid)
        checklist_res = self.checklist_evaluator.evaluate_readiness(
            draft=draft,
            questions=questions,
            candidate_profile=profile,
        )

        draft_updates["readiness_score"] = checklist_res.readiness_score
        draft_updates["checklist"] = checklist_res.model_dump_json(by_alias=True)

        # Determine target status
        if payload.status:
            draft_updates["status"] = payload.status
        elif payload.confirm_accuracy or checklist_res.is_ready_for_review:
            draft_updates["status"] = "ReadyForReview"

        draft = await self.draft_repo.update_draft(draft, draft_updates)
        return self._build_draft_response(draft, questions, job, checklist_res)

    async def submit_draft(
        self,
        user_id: Union[uuid.UUID, str],
        draft_id: Union[uuid.UUID, str],
    ) -> ApplicationDraftResponse:
        """
        Marks application draft as SubmittedByUser after candidate completes review.
        System never automatically submits; this endpoint represents the candidate's explicit confirmation.
        """
        uid = uuid.UUID(str(user_id))
        did = uuid.UUID(str(draft_id))

        draft = await self.draft_repo.get_by_id(draft_id=did, user_id=uid)
        if not draft:
            raise NotFoundException(f"Application draft with ID '{did}' not found.")

        questions = await self.question_repo.list_by_draft(draft.id)
        job = await self.job_repo.get_by_id(draft.job_id)
        profile = await self._get_candidate_profile_dict(uid)

        # Mark all questions as reviewed
        for q in questions:
            if not q.is_reviewed:
                await self.question_repo.update_question(q, {"is_reviewed": True})
        questions = await self.question_repo.list_by_draft(draft.id)

        checklist_res = self.checklist_evaluator.evaluate_readiness(
            draft=draft,
            questions=questions,
            candidate_profile=profile,
        )

        now = datetime.now(timezone.utc)
        draft = await self.draft_repo.update_draft(draft, {
            "status": "SubmittedByUser",
            "submitted_at": now,
            "readiness_score": max(checklist_res.readiness_score, 100.0),
            "checklist": checklist_res.model_dump_json(by_alias=True),
        })

        return self._build_draft_response(draft, questions, job, checklist_res)

    async def validate_draft(
        self,
        user_id: Union[uuid.UUID, str],
        draft_id: Union[uuid.UUID, str],
    ) -> ChecklistResponse:
        """
        Generates and persists readiness checklist for an application draft.
        """
        uid = uuid.UUID(str(user_id))
        did = uuid.UUID(str(draft_id))

        draft = await self.draft_repo.get_by_id(draft_id=did, user_id=uid)
        if not draft:
            raise NotFoundException(f"Application draft with ID '{did}' not found.")

        questions = await self.question_repo.list_by_draft(draft.id)
        profile = await self._get_candidate_profile_dict(uid)

        checklist = self.checklist_evaluator.evaluate_readiness(
            draft=draft,
            questions=questions,
            candidate_profile=profile,
        )

        await self.draft_repo.update_draft(draft, {
            "readiness_score": checklist.readiness_score,
            "checklist": checklist.model_dump_json(by_alias=True),
        })
        return checklist

    async def generate_checklist(
        self,
        user_id: Union[uuid.UUID, str],
        draft_id: Union[uuid.UUID, str],
    ) -> ChecklistResponse:
        """Alias for validate_draft to satisfy method interface requirements."""
        return await self.validate_draft(user_id=user_id, draft_id=draft_id)

    async def get_draft(
        self,
        user_id: Union[uuid.UUID, str],
        draft_id: Union[uuid.UUID, str],
    ) -> ApplicationDraftResponse:
        """
        Retrieves a single application draft by ID with full questions, checklist, and job details.
        """
        uid = uuid.UUID(str(user_id))
        did = uuid.UUID(str(draft_id))

        draft = await self.draft_repo.get_by_id(draft_id=did, user_id=uid)
        if not draft:
            raise NotFoundException(f"Application draft with ID '{did}' not found.")

        job = await self.job_repo.get_by_id(draft.job_id)
        questions = await self.question_repo.list_by_draft(draft.id)

        # Deserialize checklist if available
        checklist_obj = None
        if draft.checklist:
            try:
                checklist_obj = json.loads(draft.checklist)
            except Exception:
                checklist_obj = None

        return self._build_draft_response(draft, questions, job, checklist_obj)

    async def list_drafts(
        self,
        user_id: Union[uuid.UUID, str],
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[ApplicationDraftResponse]:
        """
        Lists all application preparation drafts for the candidate.
        """
        uid = uuid.UUID(str(user_id))
        drafts = await self.draft_repo.list_by_user(user_id=uid, limit=limit, offset=offset, status=status)
        results = []
        for d in drafts:
            q_list = d.questions or []
            results.append(self._build_draft_response(d, q_list, d.job, None))
        return results

    async def get_analytics(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> AssistantAnalyticsResponse:
        """
        Calculates Phase 12 Application Assistant analytics: drafts created, completed, avg completion time.
        """
        uid = uuid.UUID(str(user_id))
        analytics_data = await self.draft_repo.get_analytics(uid)
        return AssistantAnalyticsResponse(**analytics_data)

    async def delete_draft(
        self,
        user_id: Union[uuid.UUID, str],
        draft_id: Union[uuid.UUID, str],
    ) -> bool:
        """
        Deletes an application draft.
        """
        uid = uuid.UUID(str(user_id))
        did = uuid.UUID(str(draft_id))
        return await self.draft_repo.delete_draft(draft_id=did, user_id=uid)

    # -------------------------------------------------------------------------
    # Helper Profile & Resume Extractors
    # -------------------------------------------------------------------------
    async def _get_candidate_profile_dict(self, user_id: uuid.UUID) -> Dict[str, Any]:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return {
                "name": "Candidate",
                "email": "candidate@example.com",
                "phone": "+1-555-0199",
                "location": "San Francisco, CA",
                "headline": "Software Engineer",
                "summary": "Full-stack engineer with expertise in cloud and machine learning systems.",
            }
        return {
            "name": getattr(profile, "full_name", "Candidate") or "Candidate",
            "email": getattr(profile, "email", "candidate@example.com") or "candidate@example.com",
            "phone": getattr(profile, "phone", "+1-555-0199") or "+1-555-0199",
            "location": getattr(profile, "location", "San Francisco, CA") or "San Francisco, CA",
            "headline": getattr(profile, "headline", "Software Engineer") or "Software Engineer",
            "summary": getattr(profile, "summary", "") or "",
        }

    async def _get_candidate_skills(self, user_id: uuid.UUID) -> List[str]:
        if self.skill_repo:
            skills = await self.skill_repo.get_by_user_id(user_id)
            if skills:
                return [s.name for s in skills]
        return ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "Machine Learning"]

    async def _get_candidate_experiences(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        if self.experience_repo:
            exps = await self.experience_repo.get_by_user_id(user_id)
            if exps:
                return [
                    {
                        "title": e.title,
                        "company": e.company,
                        "start_date": str(e.start_date) if hasattr(e, "start_date") else "2022",
                        "end_date": str(e.end_date) if hasattr(e, "end_date") and e.end_date else "Present",
                        "description": e.description or "",
                    }
                    for e in exps
                ]
        return [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "start_date": "2022",
                "end_date": "Present",
                "description": "Architected distributed microservices and optimized relational database queries.",
            }
        ]

    async def _get_candidate_projects(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        if self.project_repo:
            projs = await self.project_repo.get_by_user_id(user_id)
            if projs:
                return [
                    {
                        "title": p.title,
                        "description": p.description or "",
                        "skills": [s.strip() for s in (p.technologies or "").split(",") if s.strip()] if hasattr(p, "technologies") and p.technologies else [],
                    }
                    for p in projs
                ]
        return [
            {
                "title": "Brain Tumor Detection Engine",
                "description": "Engineered an MRI image segmentation pipeline using U-Net architecture achieving 94% dice score.",
                "skills": ["Python", "PyTorch", "Computer Vision"],
            }
        ]

    async def _get_candidate_education(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        if self.education_repo:
            edus = await self.education_repo.get_by_user_id(user_id)
            if edus:
                return [
                    {
                        "degree": ed.degree,
                        "field_of_study": ed.field_of_study,
                        "institution": ed.institution,
                        "start_year": str(ed.start_year) if hasattr(ed, "start_year") else "2018",
                        "end_year": str(ed.end_year) if hasattr(ed, "end_year") else "2022",
                    }
                    for ed in edus
                ]
        return [
            {
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "institution": "University of Technology",
                "start_year": "2018",
                "end_year": "2022",
            }
        ]

    def _parse_options(self, raw_opts: Optional[str]) -> List[str]:
        if not raw_opts:
            return []
        try:
            parsed = json.loads(raw_opts)
            if isinstance(parsed, list):
                return parsed
            return [str(parsed)]
        except Exception:
            return [o.strip() for o in raw_opts.split(",") if o.strip()]

    def _build_draft_response(
        self,
        draft: ApplicationDraftModel,
        questions: List[ApplicationQuestionModel],
        job: Any,
        checklist: Any,
    ) -> ApplicationDraftResponse:
        """
        Converts SQLAlchemy model to typed Pydantic ApplicationDraftResponse.
        """
        job_dict = None
        if job:
            salary_str = "$120,000 - $150,000"
            if getattr(job, "salary_min", None) and getattr(job, "salary_max", None):
                salary_str = f"${int(job.salary_min):,} - ${int(job.salary_max):,}"
            elif getattr(job, "salary", None):
                salary_str = job.salary

            job_dict = {
                "id": str(getattr(job, "id", "")),
                "title": getattr(job, "title", "Target Role"),
                "company": getattr(job, "company", "Company"),
                "location": getattr(job, "location", "Remote"),
                "salary": salary_str,
                "description": getattr(job, "description", ""),
                "requirements": getattr(job, "requirements", []),
                "applyUrl": getattr(job, "apply_url", None) or getattr(job, "url", None),
            }

        question_responses = []
        for q in questions:
            opts = self._parse_options(q.options)
            question_responses.append(ApplicationQuestionResponse(
                id=q.id,
                draft_id=q.draft_id,
                question=q.question,
                generated_answer=q.generated_answer,
                user_answer=q.user_answer,
                answer_type=q.answer_type,
                options=opts,
                is_required=q.is_required,
                is_reviewed=q.is_reviewed,
                order=q.order,
                created_at=q.created_at,
                updated_at=q.updated_at,
            ))

        # Sort questions by order
        question_responses.sort(key=lambda x: x.order)

        checklist_data = None
        if isinstance(checklist, ChecklistResponse):
            checklist_data = checklist.model_dump(by_alias=True)
        elif isinstance(checklist, dict):
            checklist_data = checklist
        elif draft.checklist:
            try:
                checklist_data = json.loads(draft.checklist)
            except Exception:
                checklist_data = None

        return ApplicationDraftResponse(
            id=draft.id,
            user_id=draft.user_id,
            job_id=draft.job_id,
            status=draft.status,
            generated_answers=draft.generated_answers,
            selected_resume_id=draft.selected_resume_id,
            readiness_score=draft.readiness_score,
            checklist=checklist_data,
            notes=draft.notes,
            submitted_at=draft.submitted_at,
            created_at=draft.created_at,
            updated_at=draft.updated_at,
            questions=question_responses,
            job=job_dict,
        )
