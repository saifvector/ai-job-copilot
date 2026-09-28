"""
Pydantic v2 Schemas for Phase 11 AI Interview Preparation Platform.
Supports interview question generation, answer evaluation, mock sessions,
career coaching, and interview performance analytics with camelCase serialization.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class QuestionGenerateRequest(BaseModel):
    """Payload for generating personalized interview questions."""
    role: str = Field(..., min_length=2, max_length=255, description="Target job title or role")
    job_id: Optional[uuid.UUID] = Field(None, alias="jobId", description="Optional Job ID to ground questions in actual job description")
    preparation_type: str = Field("Comprehensive", alias="preparationType", description="HR, Technical, Behavioral, System Design, Comprehensive, Role-Specific")
    focus_areas: Optional[List[str]] = Field(None, alias="focusAreas", description="Specific technologies or focus topics (e.g. Python, AI/ML, System Design)")
    question_count: int = Field(10, alias="questionCount", ge=3, le=25, description="Number of questions to generate")

    model_config = ConfigDict(populate_by_name=True)


class QuestionResponse(BaseModel):
    """Question item representation with sample answers and candidate practice status."""
    id: uuid.UUID
    preparation_id: uuid.UUID = Field(..., alias="preparationId")
    category: str = Field(..., description="HR, Technical, Behavioral, Project-Based, Resume-Based, System Design")
    difficulty: str = Field(..., description="Easy, Medium, Hard")
    question: str
    sample_answer: str = Field(..., alias="sampleAnswer")
    explanation: str
    user_answer: Optional[str] = Field(None, alias="userAnswer")
    score: Optional[float] = None
    feedback: Optional[str] = None
    is_completed: bool = Field(False, alias="isCompleted")
    evaluated_at: Optional[datetime] = Field(None, alias="evaluatedAt")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class InterviewPreparationResponse(BaseModel):
    """Interview preparation set response with list of generated questions."""
    id: uuid.UUID
    user_id: uuid.UUID = Field(..., alias="userId")
    job_id: Optional[uuid.UUID] = Field(None, alias="jobId")
    role: str
    preparation_type: str = Field(..., alias="preparationType")
    generated_at: datetime = Field(..., alias="generatedAt")
    questions: List[QuestionResponse] = Field(default_factory=list)
    total_questions: int = Field(0, alias="totalQuestions")
    completed_questions: int = Field(0, alias="completedQuestions")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AnswerEvaluationRequest(BaseModel):
    """Request payload for evaluating candidate's answer."""
    question_id: Optional[uuid.UUID] = Field(None, alias="questionId")
    question: Optional[str] = Field(None, description="The interview question text")
    user_answer: str = Field(..., alias="userAnswer", min_length=2, description="Candidate's typed or dictated answer")
    category: Optional[str] = Field("General", description="HR, Technical, Behavioral, System Design, Project-Based")
    difficulty: Optional[str] = Field("Medium", description="Easy, Medium, Hard")
    role: Optional[str] = Field(None, description="Target role context")

    model_config = ConfigDict(populate_by_name=True)


class AnswerEvaluationResponse(BaseModel):
    """Detailed evaluation of candidate's answer."""
    question_id: Optional[uuid.UUID] = Field(None, alias="questionId")
    score: float = Field(..., ge=0.0, le=100.0, description="Numerical score out of 100")
    strengths: List[str] = Field(default_factory=list, description="Key strengths identified in the answer")
    weaknesses: List[str] = Field(default_factory=list, description="Gaps, missing keywords, or structural shortcomings")
    suggested_improvements: List[str] = Field(default_factory=list, alias="suggestedImprovements", description="Actionable recommendations to enhance the response")
    feedback: str = Field(..., description="Comprehensive summary evaluation")
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="evaluatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MockInterviewSessionSubmission(BaseModel):
    """Submission payload for completing a full mock interview session."""
    role: str = Field(..., min_length=2, max_length=255)
    preparation_id: Optional[uuid.UUID] = Field(None, alias="preparationId")
    answers: List[Dict[str, Any]] = Field(..., description="Array of question responses and answer texts")

    model_config = ConfigDict(populate_by_name=True)


class MockInterviewResponse(BaseModel):
    """Mock interview session record with aggregate performance score and feedback."""
    id: uuid.UUID
    user_id: uuid.UUID = Field(..., alias="userId")
    role: str
    score: float
    feedback: Dict[str, Any]
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SkillRecommendationDTO(BaseModel):
    """Skill recommendation item."""
    skill: str
    category: str
    priority: str = "High"  # High, Medium, Low
    action: str
    estimated_days: int = Field(7, alias="estimatedDays")

    model_config = ConfigDict(populate_by_name=True)


class RoadmapStepDTO(BaseModel):
    """Actionable study phase within the learning roadmap."""
    phase: str
    title: str
    focus: str
    duration: str
    milestones: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class CareerCoachingResponse(BaseModel):
    """Personalized career coaching guidance, readiness scoring, and roadmap."""
    role: str
    interview_readiness_score: float = Field(..., alias="interviewReadinessScore")
    strong_areas: List[str] = Field(default_factory=list, alias="strongAreas")
    weak_areas: List[str] = Field(default_factory=list, alias="weakAreas")
    skill_development_recommendations: List[Dict[str, Any]] = Field(default_factory=list, alias="skillDevelopmentRecommendations")
    learning_roadmap: List[Dict[str, Any]] = Field(default_factory=list, alias="learningRoadmap")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class InterviewAnalyticsResponse(BaseModel):
    """Candidate interview practice telemetry and performance analytics."""
    questions_completed: int = Field(..., alias="questionsCompleted")
    average_score: float = Field(..., alias="averageScore")
    weak_areas: List[str] = Field(default_factory=list, alias="weakAreas")
    strong_areas: List[str] = Field(default_factory=list, alias="strongAreas")
    total_sessions: int = Field(..., alias="totalSessions")
    readiness_score: float = Field(..., alias="readinessScore")
    category_breakdown: Dict[str, Dict[str, Any]] = Field(default_factory=dict, alias="categoryBreakdown")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
