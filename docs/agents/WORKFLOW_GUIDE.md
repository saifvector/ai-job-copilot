# Multi-Agent Workflow Engine Guide (Phase 15)

## 1. Overview

The **Workflow Engine** ([`WorkflowEngine`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/orchestration/workflow_engine.py)) coordinates sequential and interdependent multi-agent execution graphs (DAGs). Each step in a pipeline is assigned to a specialized agent, resolves upstream dependencies, enriches a cumulative shared context dictionary, and enforces step failure policies.

---

## 2. Built-in Workflow Pipelines

### 1. `resume_to_match_pipeline` (Resume-to-Match Career Pipeline)
End-to-end automation transforming an uploaded resume into ranked market matches, career analytics, and an executive briefing:

```
[Resume Uploaded]
       │
       ▼
1. ResumeAgent (ATS Scoring & Skill Extraction)
       │ (context: resume_skills, ats_score, candidate_target_role)
       ▼
2. JobDiscoveryAgent (Opportunity Aggregation & Ranking)
       │ (context: discovered_jobs, recommended_job_ids)
       ▼
3. MatchingAgent (Candidate-to-Job Fit Alignment)
       │ (context: matches, top_match_id, best_fit_score)
       ▼
4. AnalyticsAgent (Career Readiness Index & Skill Gaps)
       │ (context: analytics_summary, skill_gaps, readiness_score)
       ▼
5. ReportingAgent (Executive Summary & Action Roadmap)
       │ (context: generated_report, report_id)
       ▼
[Dashboard Update & Client Notification]
```

### 2. `application_preparation_pipeline`
Prepares outbound applications for targeted roles:
1. `JobDiscoveryAgent` (Search target postings)
2. `MatchingAgent` (Evaluate fit and extract gaps)
3. `ApplicationAgent` (Draft customized cover letter and pre-fill form questions)
4. `RecruiterAgent` (Identify hiring managers and craft outreach pitch)

### 3. `career_audit_pipeline`
Comprehensive audit of candidate readiness:
1. `ResumeAgent` (Resume ATS audit)
2. `InterviewAgent` (Technical and behavioral question simulation)
3. `AnalyticsAgent` (Market readiness and positioning analysis)
4. `ReportingAgent` (Audit synthesis and 7-day tactical plan)

---

## 3. Step Specification & Dependency Resolution

Each step in a workflow DAG conforms to the following structure:

```json
{
  "step_id": "step_candidate_matching",
  "agent": "MatchingAgent",
  "depends_on": ["step_job_discovery", "step_resume_analysis"],
  "payload": { "threshold": 80.0 },
  "on_failure": "ABORT"
}
```

* **`depends_on`**: Array of `step_id` identifiers that must complete successfully prior to this step starting.
* **`on_failure` Policies**:
  - `ABORT`: Halts pipeline execution immediately and marks the overall workflow as `FAILED`.
  - `CONTINUE`: Logs step failure, marks step as `SKIPPED` or `FAILED`, and proceeds to downstream steps.

---

## 4. State Persistence & Telemetry

Workflow executions are persisted in [`workflow_executions`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/models/workflow_execution.py):
* `workflow_type`: Template identifier.
* `status`: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`.
* `current_step`: Active step pointer.
* `steps`: JSON array containing duration, model used, and outcome summary for each executed step.
* `context`: Cumulative shared memory dictionary containing all agent outputs.
* `duration_ms`: Total execution time from start to completion.
