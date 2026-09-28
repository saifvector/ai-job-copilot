import uuid
import pytest
from httpx import AsyncClient
from models.user import UserModel


@pytest.mark.asyncio
async def test_agents_and_workflows_api_end_to_end(client: AsyncClient, db_session):
    # Setup test user
    user_id = uuid.uuid4()
    user = UserModel(
        id=user_id,
        name="Agent Platform Architect",
        email=f"agent_arch_{uuid.uuid4().hex[:8]}@example.com",
    )
    db_session.add(user)
    await db_session.commit()

    headers = {"X-User-Id": str(user_id)}

    # 1. List Registered Agents
    agents_res = await client.get("/api/v1/agents", headers=headers)
    assert agents_res.status_code == 200
    agents_data = agents_res.json()
    assert agents_data["total"] >= 8
    agent_names = [a["name"] for a in agents_data["items"]]
    assert "ResumeAgent" in agent_names
    assert "MatchingAgent" in agent_names

    # 2. Get Single Agent
    get_agent_res = await client.get("/api/v1/agents/ResumeAgent", headers=headers)
    assert get_agent_res.status_code == 200
    assert get_agent_res.json()["name"] == "ResumeAgent"

    # 3. Directly Execute an Agent
    exec_res = await client.post(
        "/api/v1/agents/ResumeAgent/execute",
        json={
            "payload": {
                "mode": "analyze",
                "target_role": "Cloud Architect",
                "skills": ["AWS", "Terraform", "Kubernetes", "Python"],
            }
        },
        headers=headers,
    )
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] == "COMPLETED"
    assert "ats_score" in exec_data["result"]

    # 4. Agent Memory Store and Retrieve
    store_mem_res = await client.post(
        "/api/v1/agents/memories",
        json={
            "agent": "ResumeAgent",
            "memory_type": "preference",
            "content": {"prefers_remote": True, "target_salary": 200000},
            "relevance_score": 0.95,
        },
        headers=headers,
    )
    assert store_mem_res.status_code == 201
    mem_data = store_mem_res.json()
    assert mem_data["agent"] == "ResumeAgent"

    list_mem_res = await client.get("/api/v1/agents/memories?agent=ResumeAgent", headers=headers)
    assert list_mem_res.status_code == 200
    assert list_mem_res.json()["total"] >= 1

    # 5. Model Router Simulation
    route_res = await client.post(
        "/api/v1/agents/model-route",
        json={
            "task_type": "deep_reasoning",
            "complexity": "HIGH",
            "speed_preference": "QUALITY",
            "cost_preference": "MAX_ACCURACY",
            "privacy_level": "CLOUD",
        },
        headers=headers,
    )
    assert route_res.status_code == 200
    route_data = route_res.json()
    assert "selected_model" in route_data

    # 6. Task System - Enqueue Task
    create_task_res = await client.post(
        "/api/v1/tasks?run_async=false",
        json={
            "agent": "JobDiscoveryAgent",
            "payload": {"query": "DevOps Engineer", "limit": 2},
        },
        headers=headers,
    )
    assert create_task_res.status_code == 201
    task_data = create_task_res.json()
    task_id = task_data["id"]
    assert task_data["agent"] == "JobDiscoveryAgent"

    # 7. List Tasks
    tasks_res = await client.get("/api/v1/tasks", headers=headers)
    assert tasks_res.status_code == 200
    assert tasks_res.json()["total"] >= 1

    # 8. Get Task Detail
    task_detail_res = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert task_detail_res.status_code == 200

    # 9. Cancel Task
    cancel_res = await client.post(f"/api/v1/tasks/{task_id}/cancel", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # 10. Retry Task
    retry_res = await client.post(f"/api/v1/tasks/{task_id}/retry", headers=headers)
    assert retry_res.status_code == 200
    assert retry_res.json()["retry_count"] >= 1

    # 11. List Workflows
    wf_res = await client.get("/api/v1/workflows", headers=headers)
    assert wf_res.status_code == 200
    wf_templates = wf_res.json()
    assert len(wf_templates) >= 3

    # 12. Get Workflow Template
    wf_temp_res = await client.get("/api/v1/workflows/resume_to_match_pipeline", headers=headers)
    assert wf_temp_res.status_code == 200
    assert wf_temp_res.json()["workflow_id"] == "resume_to_match_pipeline"

    # 13. Execute Multi-Agent Workflow
    exec_wf_res = await client.post(
        "/api/v1/workflows/execute",
        json={
            "workflow_type": "career_audit_pipeline",
            "initial_context": {
                "candidate_target_role": "Senior Cloud Architect",
                "resume_skills": ["AWS", "Terraform", "Python", "Kubernetes"],
            },
        },
        headers=headers,
    )
    assert exec_wf_res.status_code == 200
    exec_wf_data = exec_wf_res.json()
    assert exec_wf_data["status"] == "COMPLETED"
    assert exec_wf_data["completed_steps"] >= 3

    # 14. List Workflow Executions
    exec_list_res = await client.get("/api/v1/workflows/executions", headers=headers)
    assert exec_list_res.status_code == 200
    assert exec_list_res.json()["total"] >= 1

    # 15. Observability Telemetry Metrics
    metrics_res = await client.get("/api/v1/workflows/telemetry/metrics", headers=headers)
    assert metrics_res.status_code == 200
    metrics_data = metrics_res.json()
    assert "total_tasks" in metrics_data
    assert "registered_agents_count" in metrics_data
    assert metrics_data["registered_agents_count"] >= 8
