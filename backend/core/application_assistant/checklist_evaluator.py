"""
Checklist and Readiness Evaluator for Phase 12 Application Assistant.
Audits application drafts across document selection, question completion, candidate review,
and missing fields to compute an overall Readiness Score (0-100%).
"""
from typing import Any, Dict, List, Optional
from schemas.application_assistant import ChecklistItem, ChecklistResponse


class ApplicationChecklistEvaluator:
    """
    Evaluates application drafts and generates structured readiness checklists.
    """

    def evaluate_readiness(
        self,
        draft: Any,
        questions: List[Any],
        candidate_profile: Optional[Dict[str, Any]] = None,
    ) -> ChecklistResponse:
        """
        Calculates checklist items and readiness score.
        Weights:
        - Resume Selection: 25 points
        - Required Questions Answered: 35 points
        - Candidate Review & Accuracy Confirmation: 25 points
        - Profile Completeness / Missing Fields: 15 points
        Total = 100 points
        """
        items: List[ChecklistItem] = []
        missing_fields: List[str] = []
        score = 0.0

        # 1. Document / Resume Selection (25 pts)
        has_resume = bool(getattr(draft, "selected_resume_id", None))
        if has_resume:
            score += 25.0
            items.append(ChecklistItem(
                category="Document",
                label="Resume Selected",
                is_completed=True,
                details="A resume version (original or tailored) has been designated for this submission.",
            ))
        else:
            missing_fields.append("Selected Resume Document")
            items.append(ChecklistItem(
                category="Document",
                label="Resume Selection Missing",
                is_completed=False,
                details="Select either the Original Resume or a Tailored Resume variant before submitting.",
            ))

        # 2. Application Questions Answered (35 pts)
        required_questions = [q for q in questions if getattr(q, "is_required", True)]
        total_required = len(required_questions)

        if total_required == 0:
            # If no questions, automatically pass
            score += 35.0
            items.append(ChecklistItem(
                category="Questions",
                label="Application Questions",
                is_completed=True,
                details="No required application questions pending.",
            ))
        else:
            answered_required = [
                q for q in required_questions
                if (getattr(q, "user_answer", None) and getattr(q, "user_answer", "").strip())
                or (getattr(q, "generated_answer", None) and getattr(q, "generated_answer", "").strip())
            ]
            answered_count = len(answered_required)
            q_ratio = answered_count / total_required
            score += round(q_ratio * 35.0, 1)

            if answered_count == total_required:
                items.append(ChecklistItem(
                    category="Questions",
                    label="All Required Questions Answered",
                    is_completed=True,
                    details=f"All {total_required} required question(s) have valid answers.",
                ))
            else:
                missing_count = total_required - answered_count
                missing_fields.append(f"{missing_count} Required Question(s) Unanswered")
                items.append(ChecklistItem(
                    category="Questions",
                    label="Incomplete Required Questions",
                    is_completed=False,
                    details=f"{answered_count} of {total_required} required questions have answers.",
                ))

        # 3. Candidate Review Workflow (25 pts)
        reviewed_questions = [q for q in questions if getattr(q, "is_reviewed", False)]
        total_questions = len(questions)
        is_ready_status = getattr(draft, "status", "") in ("ReadyForReview", "SubmittedByUser")

        if total_questions > 0 and len(reviewed_questions) == total_questions:
            score += 25.0
            items.append(ChecklistItem(
                category="Review",
                label="Candidate Answer Review Complete",
                is_completed=True,
                details="Candidate has manually inspected and verified all generated answers.",
            ))
        elif is_ready_status or len(reviewed_questions) > 0:
            review_ratio = len(reviewed_questions) / max(total_questions, 1)
            score += round(review_ratio * 25.0, 1)
            items.append(ChecklistItem(
                category="Review",
                label="Partial Review Completed",
                is_completed=False,
                details=f"{len(reviewed_questions)} of {total_questions} answers verified by candidate.",
            ))
        else:
            items.append(ChecklistItem(
                category="Review",
                label="Candidate Review Pending",
                is_completed=False,
                details="Review and edit the AI-generated responses to ensure complete truthfulness.",
            ))

        # 4. Profile & Contact Completeness (15 pts)
        profile = candidate_profile or {}
        profile_checks = [
            ("Full Name", bool(profile.get("name"))),
            ("Email Address", bool(profile.get("email"))),
            ("Phone Number", bool(profile.get("phone"))),
            ("Location", bool(profile.get("location"))),
        ]

        passed_profile = [name for name, passed in profile_checks if passed]
        failed_profile = [name for name, passed in profile_checks if not passed]

        if not failed_profile:
            score += 15.0
            items.append(ChecklistItem(
                category="Profile",
                label="Contact Information Complete",
                is_completed=True,
                details="Candidate contact information (name, email, phone, location) is ready for auto-fill.",
            ))
        else:
            profile_score = round((len(passed_profile) / len(profile_checks)) * 15.0, 1)
            score += profile_score
            for field in failed_profile:
                missing_fields.append(f"Profile: {field}")
            items.append(ChecklistItem(
                category="Profile",
                label="Contact Information Incomplete",
                is_completed=False,
                details=f"Missing: {', '.join(failed_profile)}",
            ))

        final_score = min(100.0, max(0.0, round(score, 1)))
        is_ready = (final_score >= 80.0) and has_resume and (len(missing_fields) == 0 or all("Profile:" in m for m in missing_fields))

        return ChecklistResponse(
            readiness_score=final_score,
            is_ready_for_review=is_ready,
            items=items,
            missing_fields=missing_fields,
        )
