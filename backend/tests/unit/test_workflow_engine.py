import uuid
import pytest
from orchestration.workflow_engine import workflow_engine


@pytest.mark.asyncio
async def test_workflow_engine_builtin_templates():
    templates = workflow_engine.list_workflow_templates()
    assert len(templates) >= 3

    template_ids = [t["workflow_id"] for t in templates]
    assert "resume_to_match_pipeline" in template_ids
    assert "application_preparation_pipeline" in template_ids
    assert "career_audit_pipeline" in template_ids

    r2m = workflow_engine.get_workflow_template("resume_to_match_pipeline")
    assert r2m is not None
    assert len(r2m["steps"]) == 5
    assert r2m["steps"][0]["agent"] == "ResumeAgent"
    assert r2m["steps"][1]["agent"] == "JobDiscoveryAgent"
    assert r2m["steps"][2]["agent"] == "MatchingAgent"


@pytest.mark.asyncio
async def test_execute_resume_to_match_pipeline_end_to_end():
    initial_context = {
        "candidate_target_role": "Principal Software Engineer",
        "resume_skills": ["Python", "FastAPI", "PostgreSQL", "Kafka", "Kubernetes", "AWS"],
    }
    result = await workflow_engine.execute_workflow(
        workflow_id="resume_to_match_pipeline",
        initial_context=initial_context,
    )

    assert result["status"] == "COMPLETED"
    assert result["completed_steps"] == 5
    assert len(result["step_records"]) == 5
    assert result["total_duration_ms"] > 0

    final_ctx = result["final_context"]
    assert "resume_skills" in final_ctx
    assert "discovered_jobs" in final_ctx
    assert "matches" in final_ctx
    assert "analytics_summary" in final_ctx
    assert "generated_report" in final_ctx
    assert "step_results" in final_ctx


@pytest.mark.asyncio
async def test_workflow_dependency_failure_handling():
    # Define custom workflow with an impossible dependency
    custom_steps = [
        {
            "step_id": "step_nonexistent",
            "agent": "NonExistentAgent",
            "depends_on": [],
            "on_failure": "ABORT",
        },
        {
            "step_id": "step_child",
            "agent": "ReportingAgent",
            "depends_on": ["step_nonexistent"],
            "on_failure": "CONTINUE",
        },
    ]

    result = await workflow_engine.execute_workflow(
        workflow_id="custom_failing_workflow",
        custom_steps=custom_steps,
    )

    assert result["status"] == "FAILED"
    assert result["completed_steps"] == 0
    assert result["step_records"][0]["status"] == "FAILED"


@pytest.mark.asyncio
async def test_workflow_continue_on_failure_policy():
    custom_steps = [
        {
            "step_id": "step_recruiter",
            "agent": "RecruiterAgent",
            "depends_on": [],
            "payload": {"company": "Vercel"},
            "on_failure": "CONTINUE",
        },
        {
            "step_id": "step_reporting",
            "agent": "ReportingAgent",
            "depends_on": ["step_recruiter"],
            "payload": {"title": "Post-Recruiter Report"},
            "on_failure": "CONTINUE",
        },
    ]

    result = await workflow_engine.execute_workflow(
        workflow_id="custom_continue_workflow",
        custom_steps=custom_steps,
    )

    assert result["status"] == "COMPLETED"
    assert result["completed_steps"] == 2
