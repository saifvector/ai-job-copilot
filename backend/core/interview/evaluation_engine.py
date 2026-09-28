"""
Answer Evaluation Engine for Phase 11 AI Interview Preparation Platform.
Evaluates candidate answers across technical correctness, structure (STAR),
clarity, and completeness, producing numerical scores and actionable feedback.
"""
import json
import re
from typing import Any, Dict, List, Optional
from core.ai.orchestrator import AIOrchestrator
from core.interview.prompts import (
    ANSWER_EVALUATION_SYSTEM_PROMPT,
    build_answer_evaluation_prompt,
)
from core.logging import get_logger

logger = get_logger("interview.evaluation_engine")


class AnswerEvaluationEngine:
    """
    Evaluates candidate interview answers using AI with deterministic heuristic fallback.
    """

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None):
        self.orchestrator = orchestrator or AIOrchestrator()

    async def evaluate_answer(
        self,
        question: str,
        user_answer: str,
        sample_answer: Optional[str] = None,
        category: Optional[str] = "General",
        difficulty: Optional[str] = "Medium",
        role: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's answer and returns structured score and feedback.
        """
        prompt = build_answer_evaluation_prompt(
            question=question,
            user_answer=user_answer,
            sample_answer=sample_answer,
            category=category,
            difficulty=difficulty,
            role=role,
        )

        try:
            raw_json, telemetry = await self.orchestrator.execute_with_fallback(
                prompt=prompt,
                system_instruction=ANSWER_EVALUATION_SYSTEM_PROMPT,
            )
            parsed = json.loads(raw_json)
            if "score" in parsed and "feedback" in parsed:
                logger.info(
                    "AI answer evaluation succeeded",
                    extra={"score": parsed.get("score"), "model": telemetry.get("model_used")},
                )
                return {
                    "score": float(parsed.get("score", 75.0)),
                    "strengths": parsed.get("strengths", []),
                    "weaknesses": parsed.get("weaknesses", []),
                    "suggestedImprovements": parsed.get("suggestedImprovements", []),
                    "feedback": parsed.get("feedback", "Answer evaluated successfully."),
                }
        except Exception as exc:
            logger.warning(
                f"AI evaluation failed ({exc}). Using heuristic evaluation engine.",
                extra={"category": category, "error": str(exc)},
            )

        return self._heuristic_evaluate(
            question=question,
            user_answer=user_answer,
            category=category or "General",
            difficulty=difficulty or "Medium",
        )

    def _heuristic_evaluate(
        self,
        question: str,
        user_answer: str,
        category: str,
        difficulty: str,
    ) -> Dict[str, Any]:
        """
        Deterministic scoring and feedback heuristic based on response depth,
        vocabulary, and structural adherence.
        """
        text = user_answer.strip()
        word_count = len(text.split())

        base_score = 65.0
        strengths: List[str] = []
        weaknesses: List[str] = []
        suggested_improvements: List[str] = []

        # 1. Depth & Length Assessment
        if word_count < 12:
            base_score = 45.0
            weaknesses.append("Response is too brief to demonstrate full competence and technical depth.")
            suggested_improvements.append("Expand on your reasoning with concrete examples, edge cases, and architectural context.")
        elif word_count >= 50:
            base_score += 15.0
            strengths.append("Comprehensive response providing solid technical detail and context.")
        else:
            base_score += 5.0
            strengths.append("Clear and concise response addressing the core question.")

        # 2. Structural Assessment for Behavioral Questions (STAR)
        star_markers = {
            "situation": ["situation", "when i was", "at my previous", "in my last role", "working at"],
            "task": ["task", "responsible for", "goal was", "needed to", "had to"],
            "action": ["action", "i implemented", "i built", "i decided", "i designed", "i led"],
            "result": ["result", "outcome", "reduced", "increased", "improved", "saved", "achieved", "%"],
        }
        lower_text = text.lower()

        if category.lower() in ["behavioral", "hr"]:
            found_stars = [k for k, markers in star_markers.items() if any(m in lower_text for m in markers)]
            if len(found_stars) >= 3:
                base_score += 10.0
                strengths.append("Effective adherence to the STAR framework (Situation, Task, Action, Result).")
            else:
                weaknesses.append("Did not explicitly structure response around the full STAR methodology.")
                suggested_improvements.append("Explicitly state the Situation, Task, Action you took, and quantified Result.")

        # 3. Technical & System Design Keywords
        tech_terms = [
            "latency", "cache", "database", "index", "concurrency", "async", "thread",
            "queue", "kafka", "redis", "postgresql", "api", "rest", "graphql", "sharding",
            "microservice", "docker", "kubernetes", "memory", "cpu", "scale", "tradeoff",
            "accuracy", "metric", "loss", "model", "pipeline", "optimization", "dice", "iou", "u-net"
        ]
        matched_terms = [term for term in tech_terms if re.search(r'\b' + re.escape(term) + r'\b', lower_text)]
        if matched_terms:
            base_score += min(len(matched_terms) * 2.0, 10.0)
            strengths.append(f"Demonstrates strong domain terminology ({', '.join(matched_terms[:4])}).")
        elif category.lower() in ["technical", "system design", "project-based"]:
            weaknesses.append("Lacks specific technical keywords and system-level trade-off analysis.")
            suggested_improvements.append("Incorporate specific algorithms, system design trade-offs, and computational complexity.")

        # 4. Difficulty adjustment
        if difficulty.lower() == "hard" and word_count < 80:
            base_score -= 5.0
            suggested_improvements.append("Hard-level questions require deep exploration of failure modes and edge cases.")

        final_score = max(30.0, min(95.0, round(base_score, 1)))

        feedback = (
            f"The candidate achieved a score of {final_score}/100. "
            f"The answer {'demonstrates solid understanding' if final_score >= 75 else 'covers basic concepts but needs deeper elaboration'}. "
            f"Key focus should be on expanding quantified outcomes and edge case considerations."
        )

        return {
            "score": final_score,
            "strengths": strengths or ["Good initial framing of the answer."],
            "weaknesses": weaknesses or ["Could elaborate more on non-functional requirements."],
            "suggestedImprovements": suggested_improvements or ["Include quantified performance metrics and architectural trade-offs."],
            "feedback": feedback,
        }
