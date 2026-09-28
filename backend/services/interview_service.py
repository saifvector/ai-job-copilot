"""
InterviewService for Phase 11 AI Interview Preparation Platform.
Coordinates interview question generation, answer evaluation, mock interview sessions,
career coaching, and candidate interview performance analytics.

Methods:
- generate_questions() / generateQuestions()
- evaluate_answer() / evaluateAnswer()
- generate_mock_interview() / generateMockInterview()
- generate_roadmap() / generateRoadmap()
- get_questions()
- get_interview_history()
- get_analytics()
- get_preparation_by_id()
- delete_preparation()
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from core.exceptions import BadRequestException, NotFoundException
from core.interview.coaching_engine import CareerCoachingEngine
from core.interview.evaluation_engine import AnswerEvaluationEngine
from core.interview.question_generator import InterviewQuestionGenerator
from core.logging import get_logger
from models.interview_preparation import InterviewPreparationModel
from models.interview_question import QuestionModel
from models.mock_interview import MockInterviewModel
from repositories.candidate_intelligence_repository import (
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.interview_repository import (
    InterviewPreparationRepository,
    MockInterviewRepository,
    QuestionRepository,
)
from repositories.job_repository import JobRepository
from repositories.user_repository import UserRepository
from schemas.interview import (
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    CareerCoachingResponse,
    InterviewAnalyticsResponse,
    InterviewPreparationResponse,
    MockInterviewResponse,
    QuestionGenerateRequest,
    QuestionResponse,
)

logger = get_logger("interview.service")


class InterviewService:
    """
    Core business service for candidate AI interview preparation.
    """

    def __init__(
        self,
        prep_repo: InterviewPreparationRepository,
        question_repo: QuestionRepository,
        mock_repo: MockInterviewRepository,
        user_repo: UserRepository,
        job_repo: JobRepository,
        skill_repo: SkillRepository,
        project_repo: ProjectRepository,
        experience_repo: ExperienceRepository,
        question_generator: Optional[InterviewQuestionGenerator] = None,
        evaluation_engine: Optional[AnswerEvaluationEngine] = None,
        coaching_engine: Optional[CareerCoachingEngine] = None,
    ):
        self.prep_repo = prep_repo
        self.question_repo = question_repo
        self.mock_repo = mock_repo
        self.user_repo = user_repo
        self.job_repo = job_repo
        self.skill_repo = skill_repo
        self.project_repo = project_repo
        self.experience_repo = experience_repo
        self.question_generator = question_generator or InterviewQuestionGenerator()
        self.evaluation_engine = evaluation_engine or AnswerEvaluationEngine()
        self.coaching_engine = coaching_engine or CareerCoachingEngine()

    async def generate_questions(
        self,
        user_id: Union[uuid.UUID, str],
        request: QuestionGenerateRequest,
    ) -> InterviewPreparationResponse:
        """
        Generates personalized interview questions grounded in candidate profile and target job.
        Alias for generateQuestions().
        """
        uid = uuid.UUID(str(user_id))
        user = await self.user_repo.get_by_id(uid)
        if not user:
            raise NotFoundException(f"User {user_id} not found.")

        # 1. Fetch Candidate Intelligence (Skills, Projects, Experience)
        skills_records = await self.skill_repo.get_by_user_id(uid)
        skill_names = [s.name for s in skills_records] if skills_records else [
            "Python", "FastAPI", "React", "PostgreSQL", "Docker", "PyTorch", "System Design"
        ]

        projects_records = await self.project_repo.get_by_user_id(uid)
        projects_data = []
        for p in projects_records:
            projects_data.append({
                "title": p.title,
                "description": p.description or "",
                "technologies": p.technologies or [],
            })
        if not projects_data:
            projects_data = [{
                "title": "Brain Tumor Detection",
                "description": "Biomedical image segmentation using modified U-Net architecture with Dice loss.",
                "technologies": ["Python", "PyTorch", "OpenCV", "U-Net", "Docker"],
            }]

        experiences_records = await self.experience_repo.get_by_user_id(uid)
        experiences_data = []
        for e in experiences_records:
            experiences_data.append({
                "title": e.title,
                "company": e.company,
                "description": e.description or "",
            })

        # 2. Fetch Target Job if provided
        job_description = None
        if request.job_id:
            job = await self.job_repo.findById(request.job_id)
            if job:
                job_description = f"{job.title} at {job.company}\n\nDescription:\n{job.description}\n\nRequirements:\n{job.requirements or ''}"

        # 3. Generate Questions via AI / Domain Fallback Engine
        generated_list = await self.question_generator.generate_questions(
            role=request.role,
            preparation_type=request.preparation_type,
            skills=skill_names,
            projects=projects_data,
            experiences=experiences_data,
            job_description=job_description,
            focus_areas=request.focus_areas,
            question_count=request.question_count,
        )

        # 4. Persist Preparation Record
        prep_entity = await self.prep_repo.create({
            "user_id": uid,
            "job_id": request.job_id,
            "role": request.role,
            "preparation_type": request.preparation_type,
            "generated_at": datetime.now(timezone.utc),
        })

        # 5. Persist Questions
        questions_payload = []
        for q in generated_list:
            questions_payload.append({
                "preparation_id": prep_entity.id,
                "category": q.get("category", "General"),
                "difficulty": q.get("difficulty", "Medium"),
                "question": q.get("question", ""),
                "sample_answer": q.get("sampleAnswer", ""),
                "explanation": q.get("explanation", ""),
            })

        created_questions = await self.question_repo.create_batch(questions_payload)
        await self.prep_repo.session.commit()

        # Re-fetch eager-loaded preparation with created questions fallback
        reloaded = await self.prep_repo.findById(prep_entity.id, eager=True)
        return self._format_preparation_response(reloaded or prep_entity, questions=created_questions)

    async def evaluate_answer(
        self,
        user_id: Union[uuid.UUID, str],
        request: AnswerEvaluationRequest,
    ) -> AnswerEvaluationResponse:
        """
        Evaluates a candidate's answer to an interview question and updates practice status.
        Alias for evaluateAnswer().
        """
        uid = uuid.UUID(str(user_id))
        target_question_text = request.question or ""
        sample_answer = None
        category = request.category or "General"
        difficulty = request.difficulty or "Medium"
        question_entity: Optional[QuestionModel] = None

        if request.question_id:
            question_entity = await self.question_repo.findById(request.question_id)
            if question_entity:
                target_question_text = question_entity.question
                sample_answer = question_entity.sample_answer
                category = question_entity.category
                difficulty = question_entity.difficulty

        if not target_question_text:
            raise BadRequestException("Question text or a valid questionId must be provided for evaluation.")

        # Execute evaluation
        eval_result = await self.evaluation_engine.evaluate_answer(
            question=target_question_text,
            user_answer=request.user_answer,
            sample_answer=sample_answer,
            category=category,
            difficulty=difficulty,
            role=request.role,
        )

        score = eval_result["score"]
        strengths = eval_result["strengths"]
        weaknesses = eval_result["weaknesses"]
        improvements = eval_result["suggestedImprovements"]
        feedback_summary = eval_result["feedback"]

        # If linked to a Question entity, persist answer & score
        if question_entity:
            feedback_json = json.dumps({
                "score": score,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestedImprovements": improvements,
                "feedback": feedback_summary,
            })
            await self.question_repo.update_evaluation(
                question=question_entity,
                user_answer=request.user_answer,
                score=score,
                feedback=feedback_json,
            )
            await self.question_repo.session.commit()

        return AnswerEvaluationResponse(
            question_id=request.question_id,
            score=score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggested_improvements=improvements,
            feedback=feedback_summary,
            evaluated_at=datetime.now(timezone.utc),
        )

    async def generate_mock_interview(
        self,
        user_id: Union[uuid.UUID, str],
        role: str,
        answers: List[Dict[str, Any]],
        preparation_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> MockInterviewResponse:
        """
        Creates a completed mock interview session record with score and aggregated feedback.
        Alias for generateMockInterview().
        """
        uid = uuid.UUID(str(user_id))
        user = await self.user_repo.get_by_id(uid)
        if not user:
            raise NotFoundException(f"User {user_id} not found.")

        if not answers:
            raise BadRequestException("At least one answer must be submitted for a mock interview.")

        evaluated_answers: List[Dict[str, Any]] = []
        total_score = 0.0

        for item in answers:
            q_id = item.get("questionId") or item.get("question_id")
            q_text = item.get("question", "")
            u_ans = item.get("userAnswer") or item.get("user_answer", "")
            cat = item.get("category", "General")
            diff = item.get("difficulty", "Medium")

            eval_res = await self.evaluate_answer(
                user_id=uid,
                request=AnswerEvaluationRequest(
                    question_id=uuid.UUID(str(q_id)) if q_id else None,
                    question=q_text,
                    user_answer=u_ans or "No answer provided.",
                    category=cat,
                    difficulty=diff,
                    role=role,
                ),
            )

            evaluated_answers.append({
                "question": q_text,
                "category": cat,
                "score": eval_res.score,
                "strengths": eval_res.strengths,
                "weaknesses": eval_res.weaknesses,
                "improvements": eval_res.suggested_improvements,
            })
            total_score += eval_res.score

        avg_score = round(total_score / len(evaluated_answers), 1)

        feedback_obj = {
            "overallScore": avg_score,
            "questionsAnswered": len(evaluated_answers),
            "summary": (
                f"Candidate completed mock interview for {role} with an overall score of {avg_score}/100. "
                f"{'Performance reflects strong readiness for tech screen and on-site rounds.' if avg_score >= 80 else 'Solid performance; focus on sharpening behavioral STAR outcomes and architecture trade-offs.'}"
            ),
            "questionBreakdown": evaluated_answers,
        }

        mock_session = await self.mock_repo.create({
            "user_id": uid,
            "role": role,
            "score": avg_score,
            "feedback": json.dumps(feedback_obj),
            "created_at": datetime.now(timezone.utc),
        })
        await self.mock_repo.session.commit()

        return MockInterviewResponse(
            id=mock_session.id,
            user_id=mock_session.user_id,
            role=mock_session.role,
            score=mock_session.score,
            feedback=feedback_obj,
            created_at=mock_session.created_at,
        )

    async def generate_roadmap(
        self,
        user_id: Union[uuid.UUID, str],
        role: str,
    ) -> CareerCoachingResponse:
        """
        Generates career coaching insights, readiness score, and 4-week learning roadmap.
        Alias for generateRoadmap().
        """
        uid = uuid.UUID(str(user_id))
        skills_records = await self.skill_repo.get_by_user_id(uid)
        candidate_skills = [s.name for s in skills_records] if skills_records else [
            "Python", "FastAPI", "React", "PostgreSQL", "Docker", "PyTorch"
        ]

        completed_questions = await self.question_repo.list_by_user(
            user_id=uid,
            is_completed=True,
            limit=50,
        )
        completed_evals = []
        for q in completed_questions:
            completed_evals.append({
                "category": q.category,
                "difficulty": q.difficulty,
                "score": q.score,
            })

        mock_sessions_records = await self.mock_repo.list_by_user(user_id=uid, limit=10)
        mock_sessions_data = [{"score": m.score} for m in mock_sessions_records]

        coaching_data = self.coaching_engine.generate_coaching_insights(
            role=role,
            candidate_skills=candidate_skills,
            completed_evaluations=completed_evals,
            mock_sessions=mock_sessions_data,
        )

        return CareerCoachingResponse(
            role=coaching_data["role"],
            interview_readiness_score=coaching_data["interviewReadinessScore"],
            strong_areas=coaching_data["strongAreas"],
            weak_areas=coaching_data["weakAreas"],
            skill_development_recommendations=coaching_data["skillDevelopmentRecommendations"],
            learning_roadmap=coaching_data["learningRoadmap"],
        )

    async def get_questions(
        self,
        user_id: Union[uuid.UUID, str],
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_completed: Optional[bool] = None,
        preparation_id: Optional[Union[uuid.UUID, str]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[QuestionResponse]:
        """List candidate interview questions with optional filtering."""
        uid = uuid.UUID(str(user_id))
        questions = await self.question_repo.list_by_user(
            user_id=uid,
            category=category,
            difficulty=difficulty,
            is_completed=is_completed,
            preparation_id=preparation_id,
            limit=limit,
            offset=offset,
        )
        return [self._format_question_response(q) for q in questions]

    async def get_interview_history(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> Dict[str, Any]:
        """Returns mock interview sessions and recent interview preparations."""
        uid = uuid.UUID(str(user_id))
        mock_sessions = await self.mock_repo.list_by_user(user_id=uid, limit=20)
        preparations = await self.prep_repo.list_by_user(user_id=uid, limit=10)

        sessions_formatted = []
        for ms in mock_sessions:
            try:
                fb = json.loads(ms.feedback) if isinstance(ms.feedback, str) else ms.feedback
            except Exception:
                fb = {"summary": ms.feedback}
            sessions_formatted.append(MockInterviewResponse(
                id=ms.id,
                user_id=ms.user_id,
                role=ms.role,
                score=ms.score,
                feedback=fb,
                created_at=ms.created_at,
            ))

        preparations_formatted = [self._format_preparation_response(p) for p in preparations]

        return {
            "mockInterviews": sessions_formatted,
            "preparations": preparations_formatted,
            "totalSessions": len(sessions_formatted),
        }

    async def get_analytics(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> InterviewAnalyticsResponse:
        """Computes candidate interview practice analytics."""
        uid = uuid.UUID(str(user_id))
        completed_questions = await self.question_repo.list_by_user(
            user_id=uid,
            is_completed=True,
            limit=200,
        )
        all_questions = await self.question_repo.list_by_user(
            user_id=uid,
            limit=500,
        )
        mock_sessions = await self.mock_repo.list_by_user(user_id=uid, limit=50)

        completed_count = len(completed_questions)
        scores = [q.score for q in completed_questions if q.score is not None]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

        # Category breakdown
        category_breakdown: Dict[str, Dict[str, Any]] = {}
        for q in all_questions:
            cat = q.category
            if cat not in category_breakdown:
                category_breakdown[cat] = {"total": 0, "completed": 0, "scores": []}
            category_breakdown[cat]["total"] += 1
            if q.is_completed:
                category_breakdown[cat]["completed"] += 1
                if q.score is not None:
                    category_breakdown[cat]["scores"].append(q.score)

        strong_areas: List[str] = []
        weak_areas: List[str] = []
        for cat, data in category_breakdown.items():
            scs = data.pop("scores")
            data["averageScore"] = round(sum(scs) / len(scs), 1) if scs else 0.0
            if data["averageScore"] >= 75.0:
                strong_areas.append(f"{cat} ({data['averageScore']}%)")
            elif data["completed"] > 0:
                weak_areas.append(f"{cat} ({data['averageScore']}%)")
            else:
                weak_areas.append(f"{cat} (Not Practiced)")

        if not strong_areas:
            strong_areas = ["Core Concepts", "Problem Solving"]
        if not weak_areas:
            weak_areas = ["System Design Trade-offs", "STAR Quantified Impact"]

        # Composite readiness score
        vol_score = min(completed_count * 5.0, 100.0)
        readiness = round((avg_score * 0.5) + (vol_score * 0.3) + (min(len(mock_sessions) * 20.0, 100.0) * 0.2), 1)
        if completed_count == 0:
            readiness = 40.0

        return InterviewAnalyticsResponse(
            questions_completed=completed_count,
            average_score=avg_score,
            weak_areas=weak_areas[:5],
            strong_areas=strong_areas[:5],
            total_sessions=len(mock_sessions),
            readiness_score=readiness,
            category_breakdown=category_breakdown,
        )

    async def get_preparation_by_id(
        self,
        prep_id: Union[uuid.UUID, str],
    ) -> Optional[InterviewPreparationResponse]:
        """Fetch preparation record with all questions."""
        prep = await self.prep_repo.findById(prep_id, eager=True)
        if not prep:
            return None
        return self._format_preparation_response(prep)

    async def delete_preparation(
        self,
        prep_id: Union[uuid.UUID, str],
    ) -> bool:
        """Delete preparation record."""
        success = await self.prep_repo.delete(prep_id)
        if success:
            await self.prep_repo.session.commit()
        return success

    def _format_question_response(self, q: QuestionModel) -> QuestionResponse:
        """Formats a QuestionModel into QuestionResponse."""
        return QuestionResponse(
            id=q.id,
            preparation_id=q.preparation_id,
            category=q.category,
            difficulty=q.difficulty,
            question=q.question,
            sample_answer=q.sample_answer,
            explanation=q.explanation,
            user_answer=q.user_answer,
            score=q.score,
            feedback=q.feedback,
            is_completed=q.is_completed,
            evaluated_at=q.evaluated_at,
            created_at=q.created_at,
        )

    def _format_preparation_response(
        self,
        p: InterviewPreparationModel,
        questions: Optional[List[QuestionModel]] = None,
    ) -> InterviewPreparationResponse:
        """Formats an InterviewPreparationModel into InterviewPreparationResponse."""
        source_questions = questions if (questions is not None and len(questions) > 0) else (p.questions or [])
        questions_resp = [self._format_question_response(q) for q in source_questions]
        completed = sum(1 for q in questions_resp if q.is_completed)
        return InterviewPreparationResponse(
            id=p.id,
            user_id=p.user_id,
            job_id=p.job_id,
            role=p.role,
            preparation_type=p.preparation_type,
            generated_at=p.generated_at,
            questions=questions_resp,
            total_questions=len(questions_resp),
            completed_questions=completed,
        )
