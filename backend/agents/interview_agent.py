import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from agents.base import BaseAgent


class InterviewAgent(BaseAgent):
    """
    Specialized agent responsible for generating tailored technical and behavioral
    interview questions, simulation coaching, and STAR-method response evaluations.
    """

    @property
    def agent_name(self) -> str:
        return "InterviewAgent"

    @property
    def description(self) -> str:
        return "Generates role-specific interview questions, provides scenario coaching, and evaluates candidate responses."

    @property
    def capabilities(self) -> List[str]:
        return [
            "question_generation",
            "interview_coaching",
            "response_evaluation",
            "star_framework_scoring",
        ]

    @property
    def default_model(self) -> str:
        return "gemini-2.5-pro"

    async def _execute_internal(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        user_id: Optional[uuid.UUID],
        session: Optional[AsyncSession],
        model_used: str,
    ) -> Dict[str, Any]:
        target_role = (
            payload.get("target_role")
            or context.get("candidate_target_role")
            or context.get("target_role")
            or "Senior Software Engineer"
        )
        skills = payload.get("skills") or context.get("resume_skills") or ["Python", "FastAPI", "Distributed Systems"]
        interview_type = payload.get("type", "technical")  # technical | behavioral | system_design
        user_answer = payload.get("user_answer")
        question_eval_target = payload.get("question")

        # 1. Response Evaluation Mode if an answer is provided
        evaluation = None
        if user_answer:
            word_count = len(user_answer.split())
            has_situation = any(w in user_answer.lower() for w in ["when", "situation", "context", "at my previous"])
            has_task = any(w in user_answer.lower() for w in ["task", "needed to", "goal", "responsible for"])
            has_action = any(w in user_answer.lower() for w in ["i designed", "i built", "i implemented", "i led", "my approach"])
            has_result = any(w in user_answer.lower() for w in ["result", "reduced", "improved", "increased", "%", "saved"])

            star_score = 65.0
            if has_situation:
                star_score += 7.5
            if has_task:
                star_score += 7.5
            if has_action:
                star_score += 10.0
            if has_result:
                star_score += 10.0

            evaluation = {
                "evaluated_question": question_eval_target or "Tell me about a challenging distributed system bug you solved.",
                "response_score": round(star_score, 1),
                "star_compliance": {
                    "situation": has_situation,
                    "task": has_task,
                    "action": has_action,
                    "result": has_result,
                },
                "feedback": (
                    "Strong technical narrative. Make sure to clearly quantify the business outcome or performance improvement."
                    if not has_result
                    else "Excellent STAR framing with concrete metric outcomes."
                ),
            }

        # 2. Generate curated interview questions
        questions = [
            {
                "id": str(uuid.uuid4()),
                "category": "Architecture & Systems",
                "question": f"How do you ensure zero-downtime database migrations in high-throughput {skills[0] if skills else 'backend'} microservices?",
                "difficulty": "Hard",
                "rationale": f"Evaluates production reliability for {target_role}.",
            },
            {
                "id": str(uuid.uuid4()),
                "category": "Scalability",
                "question": "Describe your strategy for cache invalidation and distributed locking when scaling background workers.",
                "difficulty": "Medium",
                "rationale": "Assesses distributed state consistency understanding.",
            },
            {
                "id": str(uuid.uuid4()),
                "category": "Behavioral & Leadership",
                "question": "Walk me through an architectural disagreement with a peer and how you resolved it constructively.",
                "difficulty": "Medium",
                "rationale": "STAR competency on collaboration and technical diplomacy.",
            },
        ]

        coaching_tips = [
            "Use the STAR method: Situation (15%), Task (15%), Action (50%), Result (20%).",
            "Ground your answers in numbers: mention latency p99, database load reductions, or deployment frequency.",
            "Ask clarifying questions about constraints before proposing system architecture.",
        ]

        result = {
            "target_role": target_role,
            "interview_type": interview_type,
            "questions": questions,
            "coaching_tips": coaching_tips,
            "evaluation": evaluation,
            "summary": f"Generated {len(questions)} high-impact questions for {target_role} with coaching guidance.",
        }

        # Populate context for downstream agents or task chains
        context["interview_questions"] = questions
        context["coaching_tips"] = coaching_tips
        if evaluation:
            context["interview_evaluation"] = evaluation

        return result
