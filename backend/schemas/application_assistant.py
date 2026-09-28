"""
Pydantic v2 Schemas for Phase 12 Application Assistant Platform.
Provides typed schemas for application drafts, question answer generation,
checklist validation, candidate review workflow, and analytics.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ApplicationQuestionCreate(BaseModel):
    """Schema for adding a question to an application draft."""
    question: str = Field(..., min_length=2, description="Application question text")
    answer_type: str = Field("Text", alias="answerType", description="Text, YesNo, MultiSelect, Numeric")
    options: Optional[List[str]] = Field(default_factory=list, description="Available options for MultiSelect or YesNo")
    is_required: bool = Field(True, alias="isRequired")
    order: int = Field(0)

    model_config = ConfigDict(populate_by_name=True)


class ApplicationQuestionResponse(BaseModel):
    """Schema representing an application question with AI-generated and candidate answers."""
    id: uuid.UUID
    draft_id: uuid.UUID = Field(..., alias="draftId")
    question: str
    generated_answer: Optional[str] = Field(None, alias="generatedAnswer")
    user_answer: Optional[str] = Field(None, alias="userAnswer")
    answer_type: str = Field("Text", alias="answerType")
    options: List[str] = Field(default_factory=list)
    is_required: bool = Field(True, alias="isRequired")
    is_reviewed: bool = Field(False, alias="isReviewed")
    order: int = 0
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApplicationQuestionUpdate(BaseModel):
    """Schema for candidate review and edits to an answer."""
    question_id: uuid.UUID = Field(..., alias="questionId")
    user_answer: Optional[str] = Field(None, alias="userAnswer")
    is_reviewed: bool = Field(True, alias="isReviewed")

    model_config = ConfigDict(populate_by_name=True)


class ApplicationDraftCreateRequest(BaseModel):
    """Schema for initiating an application preparation draft for a target job."""
    job_id: uuid.UUID = Field(..., alias="jobId")
    selected_resume_id: Optional[uuid.UUID] = Field(None, alias="selectedResumeId")
    notes: Optional[str] = None
    custom_questions: Optional[List[ApplicationQuestionCreate]] = Field(None, alias="customQuestions")

    model_config = ConfigDict(populate_by_name=True)


class GenerateAnswersRequest(BaseModel):
    """Schema for triggering AI answer generation for application questions."""
    draft_id: uuid.UUID = Field(..., alias="draftId")
    custom_questions: Optional[List[ApplicationQuestionCreate]] = Field(None, alias="customQuestions")
    regenerate_all: bool = Field(False, alias="regenerateAll")

    model_config = ConfigDict(populate_by_name=True)


class ReviewDraftRequest(BaseModel):
    """Schema for candidate manual review, answer updates, and readiness confirmation."""
    draft_id: uuid.UUID = Field(..., alias="draftId")
    selected_resume_id: Optional[uuid.UUID] = Field(None, alias="selectedResumeId")
    answers: Optional[List[ApplicationQuestionUpdate]] = None
    notes: Optional[str] = None
    confirm_accuracy: bool = Field(False, alias="confirmAccuracy")
    status: Optional[str] = Field(None, description="Draft, ReadyForReview, SubmittedByUser, Cancelled")

    model_config = ConfigDict(populate_by_name=True)


class ChecklistItem(BaseModel):
    """Single item in the application assistant readiness checklist."""
    category: str = Field(..., description="Document, Questions, MissingFields, Profile")
    label: str
    is_completed: bool = Field(..., alias="isCompleted")
    details: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class ChecklistResponse(BaseModel):
    """Application readiness checklist and score."""
    readiness_score: float = Field(..., alias="readinessScore")
    is_ready_for_review: bool = Field(..., alias="isReadyForReview")
    items: List[ChecklistItem] = Field(default_factory=list)
    missing_fields: List[str] = Field(default_factory=list, alias="missingFields")

    model_config = ConfigDict(populate_by_name=True)


class ApplicationDraftResponse(BaseModel):
    """Complete application draft response with eager-loaded questions and job info."""
    id: uuid.UUID
    user_id: uuid.UUID = Field(..., alias="userId")
    job_id: uuid.UUID = Field(..., alias="jobId")
    status: str = Field(..., description="Draft, ReadyForReview, SubmittedByUser, Cancelled")
    generated_answers: Optional[str] = Field(None, alias="generatedAnswers")
    selected_resume_id: Optional[uuid.UUID] = Field(None, alias="selectedResumeId")
    readiness_score: float = Field(0.0, alias="readinessScore")
    checklist: Optional[Any] = None
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = Field(None, alias="submittedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    questions: List[ApplicationQuestionResponse] = Field(default_factory=list)
    job: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AssistantAnalyticsResponse(BaseModel):
    """Analytics for Application Assistant usage and completion."""
    drafts_created: int = Field(0, alias="draftsCreated")
    drafts_completed: int = Field(0, alias="draftsCompleted")
    average_completion_time_minutes: float = Field(0.0, alias="averageCompletionTimeMinutes")
    status_counts: Dict[str, int] = Field(default_factory=dict, alias="statusCounts")
    total_questions_answered: int = Field(0, alias="totalQuestionsAnswered")

    model_config = ConfigDict(populate_by_name=True)
