"""
Integration tests for AI Interview Preparation Platform REST API (Phase 11).
Validates endpoints under:
- /api/v1/interview/generate
- /api/v1/interview/evaluate
- /api/v1/interview/questions
- /api/v1/interview/history
- /api/v1/interview/mock
- /api/v1/interview/coaching
- /api/v1/interview/analytics
- /api/v1/interview/preparations/{id}
"""
import uuid
import pytest
from httpx import AsyncClient


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.UUID("a0000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_interview_api_full_flow(client: AsyncClient, mock_user_id: uuid.UUID):
    """Test full interview preparation generation, practice evaluation, mock session, and coaching."""
    headers = {"X-User-Id": str(mock_user_id)}

    # 1. Generate Interview Questions
    gen_payload = {
        "role": "Staff Full-Stack Architect",
        "preparationType": "Comprehensive",
        "focusAreas": ["React", "FastAPI", "Distributed Systems"],
        "questionCount": 6,
    }
    gen_res = await client.post("/api/v1/interview/generate", json=gen_payload, headers=headers)
    assert gen_res.status_code == 201
    prep_data = gen_res.json()["data"]
    prep_id = prep_data["id"]
    assert prep_data["role"] == "Staff Full-Stack Architect"
    assert prep_data["totalQuestions"] >= 6
    assert len(prep_data["questions"]) >= 6
    question_1 = prep_data["questions"][0]
    question_1_id = question_1["id"]

    # 2. List Questions
    list_res = await client.get("/api/v1/interview/questions", headers=headers)
    assert list_res.status_code == 200
    questions_list = list_res.json()["data"]
    assert len(questions_list) >= 6
    assert any(q["id"] == question_1_id for q in questions_list)

    # 3. Evaluate Candidate Answer
    eval_payload = {
        "questionId": question_1_id,
        "userAnswer": (
            "In my previous project at scale, we tackled database connection saturation by introducing an async connection pool "
            "with PgBouncer and an in-memory Redis cache for read-heavy entities. "
            "This brought our 99th percentile response time down from 350ms to 42ms and stabilized our service during Black Friday sales."
        ),
        "category": question_1["category"],
        "difficulty": question_1["difficulty"],
        "role": "Staff Full-Stack Architect",
    }
    eval_res = await client.post("/api/v1/interview/evaluate", json=eval_payload, headers=headers)
    assert eval_res.status_code == 200
    eval_data = eval_res.json()["data"]
    assert eval_data["score"] >= 60.0
    assert len(eval_data["strengths"]) > 0
    assert len(eval_data["suggestedImprovements"]) > 0

    # 4. Submit Full Mock Interview Session
    mock_payload = {
        "role": "Staff Full-Stack Architect",
        "preparationId": prep_id,
        "answers": [
            {
                "questionId": question_1_id,
                "question": question_1["question"],
                "userAnswer": "I implemented consistent hashing to distribute cache load across Redis nodes.",
                "category": "System Design",
                "difficulty": "Hard",
            }
        ],
    }
    mock_res = await client.post("/api/v1/interview/mock", json=mock_payload, headers=headers)
    assert mock_res.status_code == 201
    mock_data = mock_res.json()["data"]
    assert mock_data["score"] > 0.0
    assert "summary" in mock_data["feedback"]

    # 5. Get Interview History
    history_res = await client.get("/api/v1/interview/history", headers=headers)
    assert history_res.status_code == 200
    hist_data = history_res.json()["data"]
    assert "mockInterviews" in hist_data
    assert "preparations" in hist_data
    assert hist_data["totalSessions"] >= 1

    # 6. Get Career Coaching & Roadmap
    coach_res = await client.get("/api/v1/interview/coaching?role=Staff+Full-Stack+Architect", headers=headers)
    assert coach_res.status_code == 200
    coach_data = coach_res.json()["data"]
    assert "interviewReadinessScore" in coach_data
    assert len(coach_data["learningRoadmap"]) == 4
    assert len(coach_data["skillDevelopmentRecommendations"]) >= 3

    # 7. Get Interview Analytics
    analytics_res = await client.get("/api/v1/interview/analytics", headers=headers)
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()["data"]
    assert analytics_data["questionsCompleted"] >= 1
    assert analytics_data["averageScore"] > 0.0

    # 8. Get Specific Preparation Details
    prep_detail_res = await client.get(f"/api/v1/interview/preparations/{prep_id}", headers=headers)
    assert prep_detail_res.status_code == 200
    assert prep_detail_res.json()["data"]["id"] == prep_id

    # 9. Delete Preparation Pack
    delete_res = await client.delete(f"/api/v1/interview/preparations/{prep_id}", headers=headers)
    assert delete_res.status_code == 200
    assert delete_res.json()["data"] is True

    # 10. Confirm 404 after deletion
    not_found_res = await client.get(f"/api/v1/interview/preparations/{prep_id}", headers=headers)
    assert not_found_res.status_code == 404
