# AI Agent Architecture Guide (Phase 15)

## 1. Architectural Overview

Phase 15 transforms **AI Job Copilot** into an autonomous, collaborative **Multi-Agent Orchestration Platform**. Rather than executing isolated scripts or synchronous endpoints, platform capabilities are encapsulated within specialized, domain-driven AI agents that collaborate, delegate tasks, propagate shared context, and execute Directed Acyclic Graph (DAG) pipelines.

```
                  ┌──────────────────────────────────────────────┐
                  │          Internal Event Bus (Pub/Sub)        │
                  └──────┬────────────────────────────────┬──────┘
                         │                                │
        ┌────────────────▼────────────────┐      ┌────────▼──────────────┐
        │       AI Model Router           │      │    Agent Memory       │
        │ (Gemini, OpenAI, Claude, Local) │      │  (Context / Learning) │
        └────────────────┬────────────────┘      └────────┬──────────────┘
                         │                                │
    ┌────────────────────┴────────────────────────────────┴───────────────────┐
    │                       Agent Framework (BaseAgent)                       │
    ├──────────────────┬──────────────────┬──────────────────┬────────────────┤
    │   ResumeAgent    │ JobDiscoveryAgent│  MatchingAgent   │ AnalyticsAgent │
    ├──────────────────┼──────────────────┼──────────────────┼────────────────┤
    │  ReportingAgent  │  InterviewAgent  │  RecruiterAgent  │ApplicationAgent│
    └──────────────────┴──────────────────┴──────────────────┴────────────────┘
```

---

## 2. Core Agent Framework (`BaseAgent`)

Every specialized agent extends [`BaseAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/base.py) which provides standard runtime contracts:

1. **Agent Metadata & Capabilities**:
   - `agent_name`: Unique canonical identifier.
   - `description`: Role in the career acceleration lifecycle.
   - `capabilities`: List of discrete executable actions.
   - `default_model`: Default model routed for the domain (e.g. `gemini-2.5-pro` for deep reasoning, `gemini-2.5-flash` for high-throughput extraction).
   - `status`: Reactive operational state (`IDLE`, `BUSY`, `READY`).

2. **Execution Lifecycle**:
   - Resolves LLM selection via [`AIModelRouter`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/orchestration/model_router.py).
   - Injects shared context and past memories.
   - Measures exact duration in milliseconds.
   - Automatically publishes execution and failure events to the [`EventBus`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/orchestration/event_bus.py).

---

## 3. Specialized Domain Agents

### 1. [`ResumeAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/resume_agent.py)
* **Responsibilities**: Deep resume parsing, ATS compatibility scoring, keyword density extraction, and tailoring recommendations.
* **Context Contribution**: Populates `resume_skills`, `ats_score`, and `candidate_target_role` for downstream matching and application agents.

### 2. [`JobDiscoveryAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/job_discovery_agent.py)
* **Responsibilities**: Opportunity search, salary and remote filter aggregation, market listing ranking, and recommendation curation.
* **Context Contribution**: Populates `discovered_jobs` and `recommended_job_ids`.

### 3. [`MatchingAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/matching_agent.py)
* **Responsibilities**: Multidimensional skill matching, experience alignment, gap analysis, and candidate-job alignment scoring.
* **Context Contribution**: Populates `matches`, `top_match_id`, and `best_fit_score`.

### 4. [`AnalyticsAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/analytics_agent.py)
* **Responsibilities**: Career readiness indexing, market competitiveness benchmarking, primary skill gap prioritization, and funnel analytics.
* **Context Contribution**: Populates `analytics_summary`, `skill_gaps`, and `readiness_score`.

### 5. [`ReportingAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/reporting_agent.py)
* **Responsibilities**: Executive summary synthesis, 7-day tactical action plans, multi-format export packaging (JSON, Markdown, PDF).
* **Context Contribution**: Populates `generated_report` and `report_id`.

### 6. [`InterviewAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/interview_agent.py)
* **Responsibilities**: Role-tailored behavioral and technical interview questions, scenario coaching, and STAR framework answer evaluation.
* **Context Contribution**: Populates `interview_questions`, `coaching_tips`, and `interview_evaluation`.

### 7. [`RecruiterAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/recruiter_agent.py)
* **Responsibilities**: Hiring manager identification, talent acquisition tracking, cold outreach email and LinkedIn message drafting, and referral pathways.
* **Context Contribution**: Populates `recruiter_leads` and `outreach_templates`.

### 8. [`ApplicationAgent`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/agents/application_agent.py)
* **Responsibilities**: Application submission drafting, customized cover letter pitches, job portal question answering, and pre-flight QA validation.
* **Context Contribution**: Populates `application_draft` and `qa_score`.

---

## 4. Agent Memory System

Agents share persistent context across asynchronous workflows and repeated user interactions through [`AgentMemoryModel`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/models/agent_memory.py):

* **Fields**:
  - `id`: UUID primary key.
  - `user_id`: Target candidate identity.
  - `agent`: Specific agent or `*` for universal shared context.
  - `memory_type`: `preference`, `critique`, `fact`, `working_context`, `execution_output`.
  - `content`: JSON payload storing learnings, tone preferences, or previous draft revisions.
  - `relevance_score`: Weight (0.0 to 1.0) utilized for prioritized retrieval.
  - `created_at` / `updated_at`: Timestamp metadata.

---

## 5. Event Bus Integration

The [`EventBus`](file:///c:/Users/saifu/Desktop/Job%20applier/backend/orchestration/event_bus.py) provides an in-memory asynchronous Pub/Sub broker enabling reactive execution:
* **Events**:
  - `ResumeUploaded`
  - `ResumeParsed`
  - `JobsDiscovered`
  - `MatchingCompleted`
  - `ReportGenerated`
  - `WorkflowStarted` / `WorkflowCompleted`
  - `TaskCreated` / `TaskCompleted`
* **Features**:
  - Non-blocking concurrent dispatch (`asyncio.gather`).
  - Error isolation: exceptions in one subscriber do not disrupt adjacent handlers.
  - Bounded in-memory event history buffer for telemetry.
