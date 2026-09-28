"""
FastAPI Routes for Phase 11 AI Interview Preparation Platform.
Provides endpoints for:
- POST /api/v1/interview/generate -> Generate personalized questions
- POST /api/v1/interview/evaluate -> Evaluate candidate's answer
- GET  /api/v1/interview/questions -> List practice questions
- GET  /api/v1/interview/history -> Mock interview sessions & history
- POST /api/v1/interview/mock -> Submit complete mock interview session
- GET  /api/v1/interview/coaching -> Career coaching & learning roadmap
- GET  /api/v1/interview/analytics -> Interview readiness & performance analytics
- GET  /api/v1/interview/preparations/{id} -> Inspect preparation set
- DELETE /api/v1/interview/preparations/{id} -> Delete preparation set
"""
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.dependencies import get_current_user_id, get_interview_service
from schemas.common import ApiResponse
from schemas.interview import (
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    CareerCoachingResponse,
    InterviewAnalyticsResponse,
    InterviewPreparationResponse,
    MockInterviewResponse,
    MockInterviewSessionSubmission,
    QuestionGenerateRequest,
    QuestionResponse,
)
from services.interview_service import InterviewService

router = APIRouter()


@router.post(
    "/generate",
    response_model=ApiResponse[InterviewPreparationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate Interview Questions",
    description="Generate personalized interview questions grounded in candidate resume, projects, skills, and target job description.",
)
async def generate_interview_questions(
    payload: QuestionGenerateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[InterviewPreparationResponse]:
    prep = await service.generate_questions(user_id=user_id, request=payload)
    return ApiResponse(
        data=prep,
        message=f"Successfully generated {prep.total_questions} interview questions for {prep.role}.",
    )


@router.post(
    "/evaluate",
    response_model=ApiResponse[AnswerEvaluationResponse],
    status_code=status.HTTP_200_OK,
    summary="Evaluate Answer",
    description="Evaluate a candidate's answer to an interview question using AI and produce score, strengths, weaknesses, and suggestions.",
)
async def evaluate_candidate_answer(
    payload: AnswerEvaluationRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[AnswerEvaluationResponse]:
    evaluation = await service.evaluate_answer(user_id=user_id, request=payload)
    return ApiResponse(
        data=evaluation,
        message="Answer evaluated successfully.",
    )


@router.get(
    "/questions",
    response_model=ApiResponse[List[QuestionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Practice Questions",
    description="Retrieve interview practice questions with optional category, difficulty, or completion filters.",
)
async def list_interview_questions(
    category: Optional[str] = Query(None, description="Category filter (HR, Technical, Behavioral, System Design, Project-Based)"),
    difficulty: Optional[str] = Query(None, description="Difficulty filter (Easy, Medium, Hard)"),
    is_completed: Optional[bool] = Query(None, alias="isCompleted", description="Filter by completion status"),
    preparation_id: Optional[uuid.UUID] = Query(None, alias="preparationId", description="Filter by preparation set ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[List[QuestionResponse]]:
    questions = await service.get_questions(
        user_id=user_id,
        category=category,
        difficulty=difficulty,
        is_completed=is_completed,
        preparation_id=preparation_id,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        data=questions,
        message=f"Retrieved {len(questions)} interview questions.",
    )


@router.get(
    "/history",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Get Interview History",
    description="Retrieve past mock interview sessions and generated preparation sets.",
)
async def get_interview_history(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[Dict[str, Any]]:
    history = await service.get_interview_history(user_id=user_id)
    return ApiResponse(
        data=history,
        message="Interview history retrieved successfully.",
    )


@router.post(
    "/mock",
    response_model=ApiResponse[MockInterviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit Mock Interview Session",
    description="Submit answers for a full mock interview session and receive aggregated score and performance feedback.",
)
async def submit_mock_interview_session(
    payload: MockInterviewSessionSubmission,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[MockInterviewResponse]:
    mock_res = await service.generate_mock_interview(
        user_id=user_id,
        role=payload.role,
        answers=payload.answers,
        preparation_id=payload.preparation_id,
    )
    return ApiResponse(
        data=mock_res,
        message="Mock interview completed and evaluated successfully.",
    )


@router.get(
    "/coaching",
    response_model=ApiResponse[CareerCoachingResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Career Coaching & Roadmap",
    description="Retrieve interview readiness score, strong/weak areas, and a structured 4-week learning roadmap.",
)
async def get_career_coaching_insights(
    role: str = Query("Senior Full-Stack Engineer", description="Target role context for readiness scoring"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[CareerCoachingResponse]:
    coaching = await service.generate_roadmap(user_id=user_id, role=role)
    return ApiResponse(
        data=coaching,
        message="Career coaching insights and roadmap generated successfully.",
    )


@router.get(
    "/analytics",
    response_model=ApiResponse[InterviewAnalyticsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Interview Analytics",
    description="Retrieve metrics on questions completed, average score, weak areas, and strong areas.",
)
async def get_interview_analytics(
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[InterviewAnalyticsResponse]:
    analytics = await service.get_analytics(user_id=user_id)
    return ApiResponse(
        data=analytics,
        message="Interview analytics calculated successfully.",
    )


@router.get(
    "/preparations/{id}",
    response_model=ApiResponse[InterviewPreparationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Preparation Set Details",
    description="Retrieve a specific interview preparation set and its associated questions.",
)
async def get_preparation_by_id(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[InterviewPreparationResponse]:
    prep = await service.get_preparation_by_id(prep_id=id)
    if not prep or prep.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview preparation {id} not found.",
        )
    return ApiResponse(
        data=prep,
        message="Interview preparation retrieved successfully.",
    )


@router.delete(
    "/preparations/{id}",
    response_model=ApiResponse[bool],
    status_code=status.HTTP_200_OK,
    summary="Delete Preparation Set",
    description="Delete an interview preparation pack and its questions.",
)
async def delete_preparation_by_id(
    id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_current_user_id),
    service: InterviewService = Depends(get_interview_service),
) -> ApiResponse[bool]:
    prep = await service.get_preparation_by_id(prep_id=id)
    if not prep or prep.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview preparation {id} not found.",
        )
    success = await service.delete_preparation(prep_id=id)
    return ApiResponse(
        data=success,
        message="Interview preparation deleted successfully.",
    )
