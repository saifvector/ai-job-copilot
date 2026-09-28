# Career Intelligence & Outcome Learning Architecture

## 1. Executive Summary

Phase 16 transforms **AI Job Copilot** into a self-improving, feedback-driven career intelligence platform. Rather than treating job applications as one-way transactions, the platform captures empirical outcomes (recruiter screens, technical assessments, interviews, formal offers, rejections, and withdrawals) and closes the learning loop.

By systematically linking outcomes to:
- Specific tailored resume variants
- Extracted and emphasized candidate competencies
- Target employer organizations
- Application channels and match score thresholds

the system continuously generates descriptive, evidence-based recommendations that guide candidates toward higher-conversion strategies.

---

## 2. Core Architectural Pillars

```
+-----------------------------------------------------------------------------------+
|                              Candidate Experience Layer                            |
|  - Career Intelligence Dashboard        - Interactive Funnel Telemetry            |
|  - Resume Effectiveness Benchmarking    - Skill Impact Matrix & Disclaimers       |
|  - Evidence-Based Recommendations       - Outcome Event Logging Modal             |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                             Application & Outcome Pipeline                        |
|   Application Submissions ──► Outcome Events (Interviews, Assessments, Offers)    |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                        Career Intelligence Service Layer                          |
|  - CareerIntelligenceService          - OutcomeEventRepository                    |
|  - CareerRecommendationEngine         - ResumePerformanceRepository               |
|  - Skill Impact Analyzer              - SkillImpactRepository                     |
|  - Company Response Analyzer          - CareerIntelligenceSnapshotRepository      |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                             Data Warehouse & OLAP Layer                           |
|  - Outcome Events Table               - Resume Performances Table                 |
|  - Skill Impacts Table                - Career Intelligence Snapshots Table       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Data Flow & Learning Pipeline

The closed-loop learning pipeline operates through six sequential stages:

1. **Application Ingestion**: Candidate submits or logs an application tied to a target job and optional tailored resume.
2. **Outcome Event Capture**: As hiring teams respond, candidates or integrations log milestones (`InterviewReceived`, `AssessmentReceived`, `OfferReceived`, `Rejected`, `Withdrawn`).
3. **Data Collection & State Synchronization**: The `OutcomeEventRepository` captures immutable audit records, and updates the application's lifecycle state (`APPLIED`, `INTERVIEW`, `OFFER`, etc.).
4. **Analytical Aggregations**:
   - `calculate_resume_performance()` calculates empirical response rates for each tailored resume variant.
   - `calculate_skill_impact()` computes statistical correlations between skills in applied jobs and interview invitations.
   - `get_company_response_analytics()` groups response velocity and interview rates by employer.
   - `get_application_strategy_analytics()` evaluates channel yield (Referral vs. LinkedIn vs. Direct) and fit score yield tiers.
5. **Insights Synthesis**: Aggregations are translated into actionable, human-readable insights with empirical data references.
6. **Evidence-Based Recommendations**: The `CareerRecommendationEngine` produces grounded guidance categorized by `SKILL`, `RESUME`, `STRATEGY`, and `ROLE`, complete with confidence scores and recommended next steps.

---

## 4. Database Schema Specifications

### 4.1 Outcome Events (`outcome_events`)
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to `users.id`, CASCADE)
- `application_id`: UUID (Foreign Key to `applications.id`, CASCADE)
- `outcome_type`: VARCHAR(50) — `InterviewReceived`, `AssessmentReceived`, `OfferReceived`, `Rejected`, `Withdrawn`
- `occurred_at`: TIMESTAMPTZ — When the event transpired
- `notes`: TEXT — Recruiter comments or feedback
- `metadata`: TEXT (JSON) — Extra context (interview round, salary figures, technical focus)
- `created_at`: TIMESTAMPTZ

### 4.2 Resume Performance (`resume_performances`)
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to `users.id`, CASCADE)
- `tailored_resume_id`: UUID (Foreign Key to `tailored_resumes.id`, SET NULL)
- `applications_sent`: INTEGER — Total submissions using this variant
- `interviews_received`: INTEGER — Total interview invitations secured
- `offers_received`: INTEGER — Total formal offers extended
- `response_rate`: DOUBLE PRECISION — `interviews_received / applications_sent`
- `updated_at`: TIMESTAMPTZ

### 4.3 Skill Impact Matrix (`skill_impacts`)
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to `users.id`, CASCADE)
- `skill_name`: VARCHAR(100) — Unique competency name
- `interviews_influenced`: INTEGER — Count of positive interview outcomes
- `offers_influenced`: INTEGER — Count of offer outcomes
- `average_match_score`: DOUBLE PRECISION — Mean fit score across applications with this skill
- `updated_at`: TIMESTAMPTZ

### 4.4 Data Warehouse Snapshots (`career_intelligence_snapshots`)
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to `users.id`, CASCADE)
- `snapshot_date`: TIMESTAMPTZ — Point-in-time timestamp
- `total_applications`: INTEGER
- `interview_rate`: DOUBLE PRECISION
- `offer_rate`: DOUBLE PRECISION
- `rejection_rate`: DOUBLE PRECISION
- `average_response_days`: DOUBLE PRECISION
- `metrics_payload`: TEXT (JSON) — Frozen cohort breakdowns and company response profiles
- `created_at`: TIMESTAMPTZ
