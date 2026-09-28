import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from agents.registry import agent_registry
from orchestration.event_bus import AgentEvent, event_bus
from repositories.workflow_execution_repository import WorkflowExecutionRepository

logger = logging.getLogger(__name__)


# Standard Pre-Configured Multi-Agent Workflow Templates
BUILTIN_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    "resume_to_match_pipeline": {
        "workflow_id": "resume_to_match_pipeline",
        "name": "Resume-to-Match Career Pipeline",
        "description": "Orchestrates ResumeAgent -> JobDiscoveryAgent -> MatchingAgent -> AnalyticsAgent -> ReportingAgent.",
        "steps": [
            {
                "step_id": "step_resume_analysis",
                "agent": "ResumeAgent",
                "depends_on": [],
                "payload": {"mode": "analyze"},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_job_discovery",
                "agent": "JobDiscoveryAgent",
                "depends_on": ["step_resume_analysis"],
                "payload": {"limit": 5},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_candidate_matching",
                "agent": "MatchingAgent",
                "depends_on": ["step_job_discovery"],
                "payload": {},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_career_analytics",
                "agent": "AnalyticsAgent",
                "depends_on": ["step_candidate_matching"],
                "payload": {},
                "on_failure": "CONTINUE",
            },
            {
                "step_id": "step_executive_report",
                "agent": "ReportingAgent",
                "depends_on": ["step_career_analytics"],
                "payload": {"format": "json"},
                "on_failure": "CONTINUE",
            },
        ],
    },
    "application_preparation_pipeline": {
        "workflow_id": "application_preparation_pipeline",
        "name": "End-to-End Application & Outreach Pipeline",
        "description": "Orchestrates JobDiscoveryAgent -> MatchingAgent -> ApplicationAgent -> RecruiterAgent.",
        "steps": [
            {
                "step_id": "step_job_discovery",
                "agent": "JobDiscoveryAgent",
                "depends_on": [],
                "payload": {"limit": 3},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_candidate_matching",
                "agent": "MatchingAgent",
                "depends_on": ["step_job_discovery"],
                "payload": {},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_application_drafting",
                "agent": "ApplicationAgent",
                "depends_on": ["step_candidate_matching"],
                "payload": {},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_recruiter_outreach",
                "agent": "RecruiterAgent",
                "depends_on": ["step_application_drafting"],
                "payload": {},
                "on_failure": "CONTINUE",
            },
        ],
    },
    "career_audit_pipeline": {
        "workflow_id": "career_audit_pipeline",
        "name": "Comprehensive Career Readiness Audit",
        "description": "Orchestrates ResumeAgent -> InterviewAgent -> AnalyticsAgent -> ReportingAgent.",
        "steps": [
            {
                "step_id": "step_resume_audit",
                "agent": "ResumeAgent",
                "depends_on": [],
                "payload": {"mode": "analyze"},
                "on_failure": "ABORT",
            },
            {
                "step_id": "step_interview_prep",
                "agent": "InterviewAgent",
                "depends_on": ["step_resume_audit"],
                "payload": {"type": "technical"},
                "on_failure": "CONTINUE",
            },
            {
                "step_id": "step_market_analytics",
                "agent": "AnalyticsAgent",
                "depends_on": ["step_resume_audit"],
                "payload": {},
                "on_failure": "CONTINUE",
            },
            {
                "step_id": "step_final_report",
                "agent": "ReportingAgent",
                "depends_on": ["step_market_analytics"],
                "payload": {"title": "Comprehensive Career Readiness Audit"},
                "on_failure": "CONTINUE",
            },
        ],
    },
}


class WorkflowEngine:
    """
    DAG-based Multi-Agent Workflow Engine.
    Executes sequential and interdependent agent steps, resolves step dependencies,
    propagates shared memory context, and tracks comprehensive execution telemetry.
    """

    def __init__(self) -> None:
        self.builtin_workflows = BUILTIN_WORKFLOWS

    def list_workflow_templates(self) -> List[Dict[str, Any]]:
        return list(self.builtin_workflows.values())

    def get_workflow_template(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.builtin_workflows.get(workflow_id)

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_context: Optional[Dict[str, Any]] = None,
        custom_steps: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[uuid.UUID] = None,
        execution_id: Optional[uuid.UUID] = None,
        session: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """
        Executes a workflow pipeline end-to-end.
        """
        workflow_def = self.get_workflow_template(workflow_id)
        if not workflow_def and not custom_steps:
            raise ValueError(f"Unknown workflow '{workflow_id}' and no custom steps provided.")

        workflow_name = workflow_def.get("name", workflow_id) if workflow_def else "Custom Workflow"
        steps_spec = custom_steps or (workflow_def["steps"] if workflow_def else [])
        total_steps = len(steps_spec)

        execution_id = execution_id or uuid.uuid4()
        repo = WorkflowExecutionRepository(session) if session else None

        # Create or update DB record
        if repo and user_id:
            await repo.create_execution(
                execution_id=execution_id,
                user_id=user_id,
                workflow_type=workflow_id,
                steps=steps_spec,
                initial_context=initial_context or {},
            )

        await event_bus.publish(
            AgentEvent(
                event_name="WorkflowStarted",
                user_id=user_id,
                payload={
                    "execution_id": str(execution_id),
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "total_steps": total_steps,
                },
            )
        )

        shared_context = dict(initial_context or {})
        shared_context["step_results"] = {}
        completed_step_ids = set()
        step_execution_records = []
        overall_status = "COMPLETED"
        start_time = time.perf_counter()

        try:
            for step_index, step in enumerate(steps_spec):
                step_id = step.get("step_id", f"step_{step_index}")
                agent_name = step.get("agent")
                depends_on = step.get("depends_on", [])
                on_failure = step.get("on_failure", "ABORT").upper()
                step_payload = dict(step.get("payload", {}))

                # Check dependencies
                missing_deps = [dep for dep in depends_on if dep not in completed_step_ids]
                if missing_deps:
                    err_msg = f"Step '{step_id}' failed dependency check: missing {missing_deps}"
                    logger.error(f"[WorkflowEngine] {err_msg}")
                    if on_failure == "ABORT":
                        overall_status = "FAILED"
                        step_execution_records.append({
                            "step_id": step_id,
                            "agent": agent_name,
                            "status": "FAILED",
                            "error": err_msg,
                        })
                        break
                    else:
                        step_execution_records.append({
                            "step_id": step_id,
                            "agent": agent_name,
                            "status": "SKIPPED",
                            "error": err_msg,
                        })
                        continue

                agent = agent_registry.get(agent_name)
                if not agent:
                    err_msg = f"Agent '{agent_name}' is not registered."
                    logger.error(f"[WorkflowEngine] {err_msg}")
                    if on_failure == "ABORT":
                        overall_status = "FAILED"
                        step_execution_records.append({
                            "step_id": step_id,
                            "agent": agent_name,
                            "status": "FAILED",
                            "error": err_msg,
                        })
                        break
                    else:
                        continue

                # Execute step
                step_start = time.perf_counter()
                try:
                    logger.info(f"[WorkflowEngine] Running step '{step_id}' with agent '{agent_name}'")
                    agent_res = await agent.execute(
                        payload=step_payload,
                        context=shared_context,
                        user_id=user_id,
                        session=session,
                    )
                    step_duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
                    step_result_data = agent_res.get("result", {})

                    shared_context["step_results"][step_id] = step_result_data
                    completed_step_ids.add(step_id)

                    step_record = {
                        "step_id": step_id,
                        "agent": agent_name,
                        "status": "COMPLETED",
                        "duration_ms": step_duration_ms,
                        "model_used": agent_res.get("model_used"),
                        "result_summary": step_result_data.get("summary", "Step executed successfully."),
                    }
                    step_execution_records.append(step_record)

                    # Update DB progress
                    if repo:
                        await repo.update_progress(
                            execution_id=execution_id,
                            status="RUNNING",
                            current_step=step_id,
                            steps=step_execution_records,
                            context=shared_context,
                        )

                    await event_bus.publish(
                        AgentEvent(
                            event_name="WorkflowStepCompleted",
                            user_id=user_id,
                            payload={
                                "execution_id": str(execution_id),
                                "workflow_id": workflow_id,
                                "step_id": step_id,
                                "agent": agent_name,
                                "duration_ms": step_duration_ms,
                            },
                        )
                    )

                except Exception as step_exc:
                    step_duration_ms = round((time.perf_counter() - step_start) * 1000, 2)
                    err_text = str(step_exc)
                    logger.error(f"[WorkflowEngine] Step '{step_id}' failed: {err_text}", exc_info=True)

                    step_record = {
                        "step_id": step_id,
                        "agent": agent_name,
                        "status": "FAILED",
                        "duration_ms": step_duration_ms,
                        "error": err_text,
                    }
                    step_execution_records.append(step_record)

                    await event_bus.publish(
                        AgentEvent(
                            event_name="WorkflowStepFailed",
                            user_id=user_id,
                            payload={
                                "execution_id": str(execution_id),
                                "workflow_id": workflow_id,
                                "step_id": step_id,
                                "agent": agent_name,
                                "error": err_text,
                            },
                        )
                    )

                    if on_failure == "ABORT":
                        overall_status = "FAILED"
                        break

            total_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Persist completion
            if repo:
                if overall_status == "COMPLETED":
                    await repo.complete_execution(
                        execution_id=execution_id,
                        final_context=shared_context,
                        step_records=step_execution_records,
                        duration_ms=total_duration_ms,
                    )
                else:
                    await repo.fail_execution(
                        execution_id=execution_id,
                        error="One or more critical workflow steps failed.",
                        final_context=shared_context,
                        step_records=step_execution_records,
                        duration_ms=total_duration_ms,
                    )

            await event_bus.publish(
                AgentEvent(
                    event_name="WorkflowCompleted" if overall_status == "COMPLETED" else "WorkflowFailed",
                    user_id=user_id,
                    payload={
                        "execution_id": str(execution_id),
                        "workflow_id": workflow_id,
                        "status": overall_status,
                        "total_duration_ms": total_duration_ms,
                        "completed_steps": len(completed_step_ids),
                        "total_steps": total_steps,
                    },
                )
            )

            return {
                "execution_id": str(execution_id),
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "status": overall_status,
                "total_duration_ms": total_duration_ms,
                "completed_steps": len(completed_step_ids),
                "total_steps": total_steps,
                "step_records": step_execution_records,
                "final_context": shared_context,
            }

        except Exception as e:
            total_duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"[WorkflowEngine] Workflow execution encountered unhandled error: {e}", exc_info=True)
            if repo:
                await repo.fail_execution(
                    execution_id=execution_id,
                    error=str(e),
                    final_context=shared_context,
                    step_records=step_execution_records,
                    duration_ms=total_duration_ms,
                )
            raise


# Global Singleton Instance
workflow_engine = WorkflowEngine()
