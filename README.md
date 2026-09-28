# AI Job Copilot

### Enterprise Career Intelligence, Autonomous Multi-Agent Workflows, and Outcome Learning Platform

[![CI Pipeline](https://img.shields.io/badge/CI-Passing-brightgreen?style=flat-square)](https://github.com/saifvector/ai-job-copilot/actions)
[![Tests](https://img.shields.io/badge/Tests-330%20Passing-brightgreen?style=flat-square)](https://github.com/saifvector/ai-job-copilot)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15%20(App%20Router)-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-blue?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Prisma](https://img.shields.io/badge/Prisma-6.0+-darkblue?style=flat-square&logo=prisma)](https://www.prisma.io/)
[![Redis](https://img.shields.io/badge/Redis-7.0+-red?style=flat-square&logo=redis)](https://redis.io/)
[![Google Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Pro%20%2F%20Flash-orange?style=flat-square)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [System Architecture](#system-architecture)
- [Core Functional Domains](#core-functional-domains)
  - [1. Career Intelligence and Outcome Learning](#1-career-intelligence-and-outcome-learning)
  - [2. Autonomous Multi-Agent Orchestration](#2-autonomous-multi-agent-orchestration)
  - [3. Resume Intelligence and ATS Tailoring Engine](#3-resume-intelligence-and-ats-tailoring-engine)
  - [4. Candidate-Grounded Application Assistant](#4-candidate-grounded-application-assistant)
  - [5. Intelligent Interview Preparation and Coaching](#5-intelligent-interview-preparation-and-coaching)
  - [6. Multi-Provider Job Discovery and Matching Engine](#6-multi-provider-job-discovery-and-matching-engine)
  - [7. Recruiter CRM and Referral Pipeline](#7-recruiter-crm-and-referral-pipeline)
  - [8. Developer Platform, Public API, and Webhooks](#8-developer-platform-public-api-and-webhooks)
  - [9. Production Hardening, Security, and Observability](#9-production-hardening-security-and-observability)
- [Technology Stack](#technology-stack)
- [Monorepo Directory Structure](#monorepo-directory-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Database Initialization and Migrations](#database-initialization-and-migrations)
  - [Running the Services](#running-the-services)
  - [Docker Compose Deployment](#docker-compose-deployment)
- [REST API Specifications](#rest-api-specifications)
- [Testing and Quality Assurance](#testing-and-quality-assurance)
- [Documentation Index](#documentation-index)
- [Scope Boundaries and Policies](#scope-boundaries-and-policies)

---

## Executive Summary

AI Job Copilot is a modular, production-ready enterprise career automation platform designed to accelerate candidate job search lifecycles, eliminate manual application overhead, optimize resume-to-job keyword alignment, and analyze real-world hiring outcomes.

Built across 16 sequential engineering phases, the platform bridges the gap between passive candidate tracking and proactive career intelligence. By combining automated job board aggregators, deterministic Applicant Tracking System (ATS) scoring algorithms, an autonomous multi-agent swarm, structured interview simulation engines, and closed-loop outcome telemetry, AI Job Copilot continuously learns which application strategies, resume variants, and technical skills correlate with higher response and offer rates.

All code is strictly typed, covered by 330 automated tests (203 backend pytest and 127 frontend vitest tests), and architected with zero pseudocode or placeholding mocks.

---

## System Architecture

```
                                  USER INTERFACE LAYER
                                            |
               +----------------------------+----------------------------+
               |                                                         |
     Next.js 15 App Router                                     Public API Consumers
   (React 19, TypeScript, Tailwind,                          (Developer Portal, SDKs,
     shadcn/ui, Zustand, Recharts)                             External Integrations)
               |                                                         |
               +----------------------------+----------------------------+
                                            |
                                            v
                                  FASTAPI APPLICATION
                                     (Python 3.12)
                     +----------------------+----------------------+
                     |                                             |
        APPLICATION & AI SERVICES                     SECURITY & OBSERVABILITY
       - AIOrchestrator (Gemini 2.5 Pro/Flash)       - SecretKeyManager (Dual-Key JWT)
       - Dynamic Model Router                        - Refresh Token Family Rotation (RTR)
       - ATS Scoring & Tailoring Pipeline            - SlidingWindowRateLimiter
       - Autonomous Multi-Agent Swarm (8 Agents)     - Prometheus Metrics & psutil
       - Career Intelligence & Outcome Analytics     - Malware Quarantine & Magic Bytes
                     |                                             |
                     +----------------------+----------------------+
                                            |
                     +----------------------+----------------------+
                     |                      |                      |
                     v                      v                      v
           PostgreSQL 16 Engine        Redis 7 Cache        Local / S3 Storage
          (Async SQLAlchemy 2.0)    (Rate Limits, Cache)    (Partitioned Uploads)
```

### Outcome Learning Feedback Loop

```
Application Submission
         |
Outcome Milestone Event (InterviewReceived | AssessmentReceived | OfferReceived | Rejected | Withdrawn)
         |
Structured Data Collection & Audit Logging
         |
Multi-Dimensional Analytics Engine (Resumes, Skills, Companies, Strategies)
         |
Cohort & Longitudinal Trend Analysis (Data Warehouse Analytical Snapshots)
         |
Empirical Recommendation Engine (Skills to Prioritize, Resume Versions, Strategy, Target Roles)
         |
Interactive Career Intelligence Dashboard (/intelligence)
```

---

## Core Functional Domains

### 1. Career Intelligence and Outcome Learning

The platform features a closed-loop outcome learning layer that systematically captures real-world application results to generate empirical, evidence-based career insights:

- Outcome Milestone Tracking (`OutcomeEvent`): Records application milestones (`InterviewReceived`, `AssessmentReceived`, `OfferReceived`, `Rejected`, `Withdrawn`) linked to candidate profiles and tailored resume variants.
- Resume Effectiveness Benchmarking (`ResumePerformance`): Quantifies conversion rates (`responseRate`, `interviewRate`, `offerRate`) across baseline and tailored variants (A, B, C) to identify high-converting resume structures.
- Descriptive Skill Impact Matrix (`SkillImpact`): Correlates technical skills against interview invitations, offer generation, and average job match scores. Explicitly presented as descriptive analytics rather than causal guarantees.
- Company Response Velocity Analytics: Tracks median response latency, interview likelihood, and offer rates across target employers.
- Application Strategy Analysis: Correlates application volume, match score distribution tiers, and job source channels with successful outcomes.
- Empirical Recommendation Engine (`CareerRecommendationEngine`): Produces prioritized recommendations across Skills, Resumes, Strategies, and Roles, complete with quantifiable confidence ratings and factual rationale strings.
- Data Warehouse Snapshots (`CareerIntelligenceSnapshot`): Persists immutable longitudinal snapshots for cohort analysis and multi-month trend analysis.
- Telemetry Visualizations: Interactive Recharts visualizations including 30-day outcome trends, conversion funnels, resume variant benchmarks, skill correlation bars, and company response tables.

### 2. Autonomous Multi-Agent Orchestration

The system includes a production-grade multi-agent architecture:

- Base Agent Framework (`BaseAgent`): Abstract base class defining memory isolation, capability registration, structured logging, execution metrics, and lifecycle hooks (`pre_execute`, `execute`, `post_execute`).
- Eight Domain-Specific Agents:
  1. Discovery Agent: Orchestrates job board aggregation, deduplication, and indexing.
  2. Matching Agent: Executes multi-factor scoring against active candidate profiles.
  3. Tailoring Agent: Synthesizes ATS-optimized resume variants grounded in target role requirements.
  4. Application Agent: Pre-fills application drafts and evaluates completeness checklists.
  5. Interview Agent: Generates behavioral and technical question sets and grades responses.
  6. Networking Agent: Manages recruiter relationships, follow-up cadences, and referral tracking.
  7. Intelligence Agent: Analyzes application outcomes and updates conversion models.
  8. Research Agent: Analyzes target company profiles, funding stages, and market presence.
- Directed Acyclic Graph (DAG) Workflow Engine (`WorkflowEngine`): Resolves step dependencies, executes steps sequentially or concurrently, handles failure policies (`FAIL_FAST`, `CONTINUE_ON_FAILURE`, `RETRY`), and propagates shared context.
- Dynamic Multi-Model Router (`ModelRouter`): Routes tasks dynamically between Google Gemini (2.5 Pro / Flash), OpenAI (GPT-4o / GPT-4o-mini), Anthropic Claude (3.5 Sonnet / 3.5 Haiku), NVIDIA Nemotron, and local Ollama instances based on complexity, latency, cost constraints, and privacy flags.
- Asynchronous In-Memory Event Bus (`EventBus`): Facilitates decoupled inter-agent communication, broadcast events, and wildcard subscriptions.

### 3. Resume Intelligence and ATS Tailoring Engine

- Deterministic Parsing: Stream-based text extraction for PDF and DOCX documents with UTF-8 normalization, noise reduction, and metadata extraction.
- Structured AI Extraction: Google Gemini 2.5 Pro structures raw resumes into strict Pydantic schemas (Contact Info, Work History, Education, Certifications, Categorized Skills).
- Deterministic 5-Factor ATS Scoring Engine: Evaluates resumes across Keyword Coverage (35%), Work Experience Relevance (25%), Role Title Alignment (15%), Education Level (10%), and Skills Overlap (15%).
- Anti-Hallucination Guardrails: Algorithmic checks ensure tailored resumes never invent unearned credentials, unworked dates, or fabricated achievements.
- Multi-Format Export: In-memory document generation producing ATS-compliant PDF, DOCX, and Markdown files.

### 4. Candidate-Grounded Application Assistant

- Pre-Fill & Packaging: Assembles candidate details, contact links, and tailored resume versions for rapid application execution.
- Truthfulness Enforcement: Answers common application questions (e.g., motivation, significant projects, salary expectations, notice period) strictly grounded in verified profile data.
- Candidate Review Mandate: Enforces human-in-the-loop review. Applications cannot be submitted automatically; candidates must review and confirm answers before submission.
- Readiness Audit: Calculates a 0-100% readiness score with actionable checklist indicators identifying missing fields or incomplete responses.

### 5. Intelligent Interview Preparation and Coaching

- Contextual Question Generation: Creates tailored technical, behavioral, and situational questions derived from the specific job posting and candidate background.
- Automated Answer Grading: Evaluates user responses on a 1-100 scale, scoring Relevance, Clarity, Depth, and Structure (STAR method compliance) with specific improvement advice.
- Mock Interview Simulation: Interactive practice sessions with real-time countdown timers, progress indicators, and session summary reports.
- Structured Coaching Roadmaps: Generates 4-week preparation plans prioritizing identified skill deficiencies.

### 6. Multi-Provider Job Discovery and Matching Engine

- Extensible Provider Architecture: Pluggable crawlers supporting RemoteOK, Greenhouse, Lever, and Wellfound with unified data normalization.
- In-Memory Deduplication: SHA-256 fingerprinting on normalized job titles, company names, and locations prevents duplicate listings.
- Automated Scheduling: APScheduler runs automated background aggregation pipelines on a 6-hour interval.
- 6-Factor Composite Match Engine: Compares candidate profiles to job specifications across Skill Overlap, Experience Depth, Role Similarity, Location Preference, Education Requirement, and Semantic Fit. Benchmark verified to score 500 jobs in under 2 seconds.

### 7. Recruiter CRM and Referral Pipeline

- Contact Relationship Management: Tracks recruiter records, firm affiliations, communication channels, and interaction histories.
- Follow-up Cadence Reminders: Tracks response status and generates automated reminders for pending follow-ups.
- Referral Lifecycle Management: Tracks referrals through a 5-stage pipeline (`Identified`, `Requested`, `Referred`, `Applied`, `Interviewed`).
- Networking Analytics: Measures outreach response rates, touchpoint velocity, and channel effectiveness.

### 8. Developer Platform, Public API, and Webhooks

- Public API (`/api/public/v1/*`): Secure endpoints enabling external programmatic access to profiles, tailored resumes, match results, applications, and reports.
- Granular Scope Authorization: Fine-grained token scopes (`read:profile`, `read:matches`, `read:applications`, `write:applications`, etc.).
- Cryptographic API Key Management: Issues hashed `ajc_live_*` API keys with SHA-256 storage, prefix indexing, and usage tracking.
- Webhook Delivery System: Real-time event notifications with HMAC-SHA256 signature verification (`t=...,v1=...`), exponential backoff retries, and comprehensive delivery logging.
- Pluggable Extension SDK (`BasePlugin`): Allows developers to register custom job aggregators, analytical exporters, and scoring algorithms.

### 9. Production Hardening, Security, and Observability

- Secret Key Rotation: Dual-key JWT architecture (`SecretKeyManager`) allowing non-disruptive key rotation without invalidating active candidate sessions.
- Refresh Token Rotation (RTR): Generates fresh token pairs per refresh cycle and instantly revokes compromised token families upon reuse detection.
- Distributed Rate Limiting: Memory-efficient sliding-window log rate limiter with differentiated tier thresholds for authentication, AI, and data endpoints.
- Upload Quarantine Pipeline: Sniffs file magic bytes to verify MIME authenticity and isolates suspicious payloads away from the primary storage pool.
- Telemetry & Metrics: Standardized Prometheus metric exposition (`GET /metrics`) tracking request counts, p50/p95/p99 latency distributions, and system resource consumption (CPU, RAM, database connection pool statistics).

---

## Technology Stack

### Frontend Architecture

| Component | Technology | Description |
|---|---|---|
| Framework | Next.js 15 (App Router) | Server and Client Components, nested layouts, static/dynamic optimization |
| UI Library | React 19 | Hooks, Suspense, concurrent rendering features |
| Language | TypeScript 5 | Strict type checking with zero `any` declarations |
| Styling | Tailwind CSS | Semantic CSS variables, dark and light theme tokens |
| Components | shadcn/ui & Radix UI | Accessible, headless WAI-ARIA compliant UI primitives |
| State Management | Zustand | Modular stores with persistence, optimistic updates, and devtools |
| Data Visualization | Recharts | Real-time charts, conversion funnels, radar charts, and trend graphs |
| Iconography | Lucide React | Tree-shakeable SVG icon collection |
| Unit Testing | Vitest & Testing Library | Fast unit and integration tests under `jsdom` |

### Backend Architecture

| Component | Technology | Description |
|---|---|---|
| Framework | FastAPI | Asynchronous ASGI framework with auto-generated OpenAPI documentation |
| Server | Uvicorn | High-throughput asynchronous ASGI web server |
| Language | Python 3.12 | Modern async/await semantics, strict typing, and high performance |
| Data Validation | Pydantic v2 | High-speed C-Rust serialization and strict schema validation |
| Async ORM | SQLAlchemy 2.0 | Declarative asynchronous database access and relation mapping |
| Migrations | Prisma & Alembic | Declarative schema definitions and versioned raw SQL migrations |
| Primary Database | PostgreSQL 16 | Relational store with foreign keys, JSONB fields, and performance indexes |
| Test Database | SQLite (aiosqlite) | Zero-configuration asynchronous in-memory testing database |
| Caching & Rate Limiting | Redis & aioredis | Distributed cache layer and sliding-window rate limit store |
| Task Scheduling | APScheduler | In-process cron scheduling for continuous job aggregation |
| Task Queue | Celery / Async Queue | Distributed asynchronous background worker processes |

### AI and Document Processing

| Component | Technology | Description |
|---|---|---|
| Primary Foundation Models | Google Gemini 2.5 Pro & Flash | Structured extraction, ATS tailoring, interview grading, application answers |
| Dynamic Model Router | Multi-Model Abstraction | Dynamic fallback across Gemini, OpenAI, Claude, Nemotron, and Ollama |
| PDF Extraction | pypdf | Non-blocking stream-based text and metadata extraction |
| Word Document Engine | python-docx | In-memory DOCX parsing and structured resume generation |
| PDF Generation | ReportLab | Programmatic vector PDF generation for resumes and executive reports |
| Spreadsheet Engine | openpyxl | Multi-sheet Excel workbook compilation |

---

## Monorepo Directory Structure

```text
ai-job-copilot/
├── frontend/                     # Next.js 15 App Router Frontend
│   ├── app/                      # Route layouts and pages
│   │   ├── applications/         # Phase 8: Application Tracking Dashboard
│   │   ├── intelligence/         # Phase 16: Career Intelligence & Outcome Analytics
│   │   ├── interview/            # Phase 11: Interview Preparation & Mock Sessions
│   │   ├── jobs/                 # Phase 4: Job Discovery Engine
│   │   ├── matching/             # Phase 5: Multi-Factor Candidate Matcher
│   │   ├── recruiters/           # Phase 9: Recruiter CRM & Networking Hub
│   │   ├── reports/              # Phase 10: Executive Analytics & Reports
│   │   ├── resume/               # Phase 2: Resume Management & Upload
│   │   │   ├── analysis/         # Phase 3: Resume Intelligence Breakdown
│   │   │   └── tailoring/        # Phase 7: ATS Resume Tailoring Engine
│   │   └── settings/             # System and Account Settings
│   ├── components/               # Design system, layout, and shared components
│   ├── features/                 # Modular feature components for each domain
│   ├── hooks/                    # Custom React hooks (theme, debounce, disclosure)
│   ├── services/                 # Strongly typed API client methods
│   ├── store/                    # Zustand state management stores
│   ├── types/                    # TypeScript interfaces and domain types
│   └── __tests__/                # Vitest unit and store test suites
│
├── backend/                      # FastAPI Python 3.12 Backend
│   ├── agents/                   # Phase 14: Multi-Agent Swarm (8 domain agents)
│   ├── api/                      # API routing layer
│   │   ├── public/v1/            # Phase 15: Public Developer API endpoints
│   │   └── v1/                   # Phase 1-16 Application API endpoints
│   ├── core/                     # Foundational subsystems
│   │   ├── ai/                   # Google Gemini & Model Router integrations
│   │   ├── jobs/                 # Ingestion pipeline, providers, and scheduler
│   │   ├── matching/             # Multi-factor candidate scoring engine
│   │   ├── security/             # Secret rotation, rate limiting, and quarantine
│   │   └── storage/              # Local and cloud storage provider abstractions
│   ├── integrations/             # Phase 15: Third-party OAuth and webhook handlers
│   ├── middleware/               # Correlation ID, timing, CSRF, and error middleware
│   ├── models/                   # SQLAlchemy async declarative models
│   ├── orchestration/            # DAG workflow engine and event bus
│   ├── plugins/                  # Plugin registry and extensible hooks
│   ├── repositories/             # Database access repository pattern implementations
│   ├── schemas/                  # Pydantic v2 validation models
│   ├── services/                 # Domain business logic services
│   └── tests/                    # Pytest test suite (unit, integration, load)
│
├── database/                     # Database schemas and migration files
│   └── prisma/
│       ├── migrations/           # Version-controlled raw SQL migrations
│       └── schema.prisma         # Declarative Prisma schema definition
│
├── docs/                         # Platform technical documentation
│   ├── agents/                   # Agent swarm and workflow engine manuals
│   ├── developer/                # Public API, webhook, and plugin documentation
│   ├── intelligence/             # Outcome tracking and analytics methodology
│   └── runbooks/                 # Production operations and disaster recovery guides
│
├── k8s/                          # Production Kubernetes manifests
├── docker-compose.yml            # Local development orchestration
├── docker-compose.prod.yml       # Production multi-stage deployment
└── README.md                     # Platform overview and instructions
```

---

## Getting Started

### Prerequisites

Ensure the following tools are installed on your workstation:

- Python 3.12+
- Node.js 20.x or 22.x LTS
- PostgreSQL 16+ (or Docker)
- Redis 7+ (optional for local development, in-memory fallback enabled)
- Git

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/saifvector/ai-job-copilot.git
   cd ai-job-copilot
   ```

2. Configure backend environment:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Provide valid configuration values in `backend/.env`:
   ```ini
   DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/job_copilot"
   TEST_DATABASE_URL="sqlite+aiosqlite:///:memory:"
   REDIS_URL="redis://localhost:6379/0"
   GEMINI_API_KEY="your-google-gemini-api-key"
   JWT_SECRET_KEY="your-primary-jwt-secret-key"
   JWT_PREVIOUS_SECRET_KEY="your-secondary-jwt-secret-key"
   ```

3. Configure frontend environment:
   ```bash
   cp frontend/.env.example frontend/.env.local
   ```
   Verify the API target:
   ```ini
   NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
   ```

### Database Initialization and Migrations

1. Install root dependencies and generate Prisma clients:
   ```bash
   npm install
   npx prisma generate --schema=database/prisma/schema.prisma
   ```

2. Execute PostgreSQL database migrations:
   ```bash
   npx prisma migrate deploy --schema=database/prisma/schema.prisma
   ```

3. (Optional) Populate database with initial seed data:
   ```bash
   npm run seed
   ```

### Running the Services

#### Option A: Running Locally in Separate Terminals

1. Start the FastAPI backend:
   ```bash
   # In terminal 1
   cd backend
   python -m venv venv
   source venv/bin/activate       # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Start the Next.js frontend:
   ```bash
   # In terminal 2
   cd frontend
   npm install
   npm run dev
   ```

3. Access the applications:
   - Frontend Dashboard: `http://localhost:3000`
   - Career Intelligence Dashboard: `http://localhost:3000/intelligence`
   - FastAPI Interactive Swagger Docs: `http://localhost:8000/docs`
   - OpenAPI Specification: `http://localhost:8000/openapi.json`
   - Prometheus Metrics Endpoint: `http://localhost:8000/metrics`

#### Option B: Automated Monorepo Scripts

- Windows:
  ```cmd
  scripts\dev.bat
  ```
- Linux / macOS:
  ```bash
  chmod +x scripts/*.sh
  ./scripts/dev.sh
  ```

### Docker Compose Deployment

Run the complete multi-container stack (PostgreSQL, Redis, Backend API, Worker, Frontend) with a single command:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## REST API Specifications

The backend exposes fully typed REST endpoints partitioned by domain:

### Career Intelligence & Outcomes (`/api/v1/intelligence/*`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/intelligence/overview` | High-level outcome KPIs, active recommendations, and funnel preview |
| `GET` | `/api/v1/intelligence/outcomes` | Filtered timeline of candidate outcome milestones |
| `POST` | `/api/v1/intelligence/outcomes` | Record a new application outcome event with audit logging |
| `GET` | `/api/v1/intelligence/analytics` | Funnel conversion rates, rejection ratios, and time-to-response metrics |
| `GET` | `/api/v1/intelligence/skills` | Descriptive skill correlation matrix with sample sizes and disclaimer |
| `GET` | `/api/v1/intelligence/resumes` | Resume variant effectiveness benchmarks across tailored variants |
| `GET` | `/api/v1/intelligence/companies` | Company response velocity, interview rates, and offer likelihood |
| `GET` | `/api/v1/intelligence/strategy` | Match score tier performance and application channel yield analysis |
| `GET` | `/api/v1/intelligence/recommendations` | Data-grounded recommendations across Skill, Resume, Strategy, and Role |
| `GET` | `/api/v1/intelligence/trends` | 30-day historical time-series analytics |
| `POST` | `/api/v1/intelligence/snapshots` | Capture immutable data warehouse snapshot for cohort tracking |

### Autonomous Multi-Agent Swarm (`/api/v1/agents/*`, `/api/v1/workflows/*`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/agents` | List all 8 registered agents with capabilities and execution metrics |
| `GET` | `/api/v1/agents/{id}` | Inspect specific agent operational state, metrics, and short-term memory |
| `POST` | `/api/v1/agents/{id}/execute` | Dispatch task directly to an individual agent |
| `POST` | `/api/v1/workflows/run` | Execute multi-step DAG workflow pipeline with dependency resolution |
| `GET` | `/api/v1/workflows/{id}` | Retrieve real-time DAG execution state, step records, and output payloads |

### Core Application Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/resume/parse` | Parse uploaded resume document with Gemini 2.5 Pro |
| `POST` | `/api/v1/resume/tailor` | Synthesize job-specific tailored resume variant (A, B, C) |
| `POST` | `/api/v1/matching/run` | Run multi-factor matching engine against active job listings |
| `POST` | `/api/v1/application-assistant/create` | Initialize grounded job application preparation draft |
| `POST` | `/api/v1/interview/generate` | Generate contextual interview question sets |
| `POST` | `/api/v1/interview/evaluate` | Grade candidate interview answer with STAR-format scoring |
| `POST` | `/api/v1/reports/generate` | Compile executive career analytics report (PDF, Excel, CSV) |

---

## Testing and Quality Assurance

The codebase enforces strict testing standards across both backend and frontend layers, totaling **330 passing automated tests**:

```bash
# Execute backend test suite (203 tests)
python -m pytest backend/tests/ -v

# Execute frontend test suite (127 tests)
cd frontend && npm test

# Validate frontend TypeScript types
cd frontend && npm run type-check

# Run linters
npm run lint
```

### Verified Test Suite Breakdown (330 Passing Tests)

1. `backend/tests/unit/test_recommendation_engine.py` — Multi-faceted heuristic recommendation generation across SKILL, RESUME, STRATEGY, and ROLE dimensions.
2. `backend/tests/unit/test_career_intelligence_service.py` — Outcome logging, funnel conversion analytics, tailored resume response benchmarking, skill impact matrix, company velocity analytics, and warehouse snapshots.
3. `backend/tests/integration/test_career_intelligence_api.py` — End-to-end FastAPI `/api/v1/intelligence/*` endpoint tests.
4. `frontend/__tests__/intelligence-store.test.ts` — Zustand `intelligenceStore` tests for state hydration, overview fetching, outcome filtering, asynchronous event logging, and snapshots.
5. `backend/tests/unit/test_agent_framework.py` — Multi-agent framework, `BaseAgent`, `AgentRegistry`, and all 8 specialized agents.
6. `backend/tests/unit/test_workflow_engine.py` — DAG multi-agent workflow pipelines, step dependency resolution, and context passing.
7. `backend/tests/unit/test_model_router.py` — Dynamic LLM routing by complexity, latency, cost, and privacy.
8. `backend/tests/unit/test_event_bus.py` — Asynchronous in-memory event bus and wildcard subscribers.
9. `backend/tests/integration/test_agents_and_workflows_api.py` — Endpoints for `/api/v1/agents`, `/api/v1/tasks`, and `/api/v1/workflows`.
10. `frontend/__tests__/agent-store.test.ts` — Zustand agentStore for agents, memories, direct execution, and model routing.
11. `frontend/__tests__/workflow-store.test.ts` — Zustand workflowStore for DAG pipelines, step records, and telemetry metrics.
12. `frontend/__tests__/task-store.test.ts` — Zustand taskStore for background async tasks, retries, and cancellations.
13. `backend/tests/unit/test_security_service.py` — JWT signing, dual-key rotation, token blacklist, refresh token family rotation, rate limiter, and quarantine isolation.
14. `backend/tests/unit/test_database_health_service.py` — Database ping, pool statistics, and migration safety validation.
15. `backend/tests/unit/test_backup_service.py` — Atomic snapshot creation, SHA-256 manifest verification, and restore procedures.
16. `backend/tests/unit/test_ai_cost_service.py` — Token accounting, model cost calculations, and user budget caps.
17. `backend/tests/unit/test_cache_service.py` — Redis and InMemory cache operations, TTL expiration, and invalidation.
18. `backend/tests/integration/test_health_and_system_api.py` — Health endpoints, Prometheus metrics (`/metrics`), and backup APIs.
19. `backend/tests/load/test_load_and_performance.py` — Request throughput benchmarks and p95 latency verification (< 300ms).
20. `backend/tests/unit/test_application_assistant_service.py` — Draft creation, question answering, candidate review workflow, and checklist scoring.
21. `backend/tests/integration/test_application_assistant_api.py` — End-to-end Application Assistant FastAPI routes.
22. `frontend/__tests__/application-assistant-store.test.ts` — Zustand store draft initialization, answer mutations, and submission.
23. `backend/tests/unit/test_interview_service.py` — Question generation, answer evaluation, mock interview sessions, and coaching roadmap generation.
24. `backend/tests/integration/test_interview_api.py` — End-to-end interview practice, question query, and analytics endpoints.
25. `frontend/__tests__/interview-store.test.ts` — Zustand interview store, practice timer controls, and mock simulation.
26. `backend/tests/unit/test_recruiter_service.py` — Recruiter CRM, interaction tracking, and referral lifecycle formulas.
27. `backend/tests/integration/test_recruiters_api.py` — End-to-end recruiter, interaction, and referral endpoints.
28. `frontend/__tests__/recruiter-store.test.ts` — Zustand recruiter store, touchpoint updates, and referral board transitions.
29. `backend/tests/unit/test_report_service.py` — Report generation engine with PDF, XLSX, CSV, and JSON exporters.
30. `backend/tests/integration/test_reports_api.py` — End-to-end report generation, download tracking, and history endpoints.
31. `frontend/__tests__/report-store.test.ts` — Zustand report store, generation mutations, and download counters.
32. `backend/tests/unit/test_application_service.py` — Application status state machine and pipeline analytics.
33. `backend/tests/integration/test_applications_api.py` — End-to-end applications, status update, and pipeline endpoints.
34. `frontend/__tests__/application-store.test.ts` — Zustand application store, optimistic status updates, and rollback logic.
35. `backend/tests/unit/test_ats_engine.py` — ATS 5-factor scoring algorithms and keyword coverage calculation.
36. `backend/tests/unit/test_resume_tailoring_service.py` — Tailoring pipeline and repository persistence.
37. `backend/tests/integration/test_resume_tailoring_api.py` — End-to-end tailored resume generation, variant switching, and export.
38. `frontend/__tests__/tailored-resume-store.test.ts` — Zustand tailored resume store, version switching, and document export.
39. `backend/tests/unit/test_analytics_service.py` — Profile health calculation, career readiness scoring, and skill gap analysis.
40. `backend/tests/integration/test_dashboard_api.py` — Dashboard analytics, readiness metrics, and snapshot endpoints.
41. `frontend/__tests__/dashboard-store.test.ts` — Zustand dashboard store and KPI state management.
42. `frontend/__tests__/analytics-store.test.ts` — Zustand analytics store, chart fetching, and snapshot capture.
43. `backend/tests/unit/test_matching_engine_and_performance.py` — Multi-factor engine weights and 500-job performance benchmark (< 2s).
44. `backend/tests/integration/test_matching_api.py` — Matching run, top matches, and score analysis endpoints.
45. `frontend/__tests__/matching-store.test.ts` — Zustand matching store, batch score filters, and candidate selection.
46. `backend/tests/unit/test_job_providers.py` — RemoteOK, Greenhouse, Lever, and Wellfound crawlers with error resilience.
47. `backend/tests/unit/test_job_normalization_and_dedup.py` — Normalizer, sanitizer, and SHA-256 deduplicator.
48. `backend/tests/integration/test_job_api.py` — Job search, filtering, pagination, and sync trigger endpoints.
49. `frontend/__tests__/job-store.test.ts` — Zustand job store and search filter state.
50. `backend/tests/unit/test_api_key_service.py` — API key generation, prefix indexing, rate limiting, and scope validation.
51. `backend/tests/unit/test_webhook_service.py` — Webhook subscriptions, HMAC signatures, and retry dispatch.
52. `backend/tests/integration/test_public_api.py` — Public API v1 endpoints and telemetry logging.
53. `backend/tests/integration/test_developer_and_webhooks_api.py` — Developer portal, key rotation, and delivery logs.
54. `frontend/__tests__/developer-store.test.ts` — Zustand developerStore, secret rotation, and analytics.
55. `frontend/__tests__/webhook-store.test.ts` — Zustand webhookStore and delivery log inspector.
56. `frontend/__tests__/integration-store.test.ts` — Zustand integrationStore and OAuth provider state.

---

## Documentation Index

Detailed architectural references, operations runbooks, and developer manuals:

- [Career Intelligence Architecture Guide](docs/intelligence/CAREER_INTELLIGENCE_ARCHITECTURE.md) — Outcome learning pipeline, data models, repository design, and analytical snapshot warehouse.
- [Outcome Tracking Guide](docs/intelligence/OUTCOME_TRACKING_GUIDE.md) — Event logging taxonomy, manual and automated ingestion, and audit trail specifications.
- [Analytics Methodology Guide](docs/intelligence/ANALYTICS_METHODOLOGY.md) — Funnel calculations, non-causal correlation formulas, confidence scoring, and recommendation heuristics.
- [Agent Architecture Guide](docs/agents/AGENT_ARCHITECTURE_GUIDE.md) — Multi-agent swarm design, BaseAgent framework, capabilities, memory system, and event bus.
- [Workflow Engine Guide](docs/agents/WORKFLOW_GUIDE.md) — DAG pipeline specifications, step dependencies, failure policies, and context propagation.
- [Model Routing Guide](docs/agents/MODEL_ROUTING_GUIDE.md) — Dynamic LLM selection across Gemini, OpenAI, Claude, Nemotron, and Ollama.
- [Developer Documentation](docs/developer/DEVELOPER_DOCUMENTATION.md) — Architecture, authentication, rate limiting, and security best practices.
- [Public API Reference (v1)](docs/developer/API_REFERENCE.md) — Complete endpoint reference for `/api/public/v1/*` with schemas and request examples.
- [Webhook Integration Guide](docs/developer/WEBHOOK_GUIDE.md) — Outbound events, HMAC-SHA256 signature verification in Node.js and Python.
- [Plugin SDK Development Guide](docs/developer/PLUGIN_DEVELOPMENT_GUIDE.md) — Lifecycle hooks, manifest declarations, and custom provider development.
- [Production Runbook](docs/runbooks/PRODUCTION_RUNBOOK.md) — Topology, service start/stop SOPs, secret rotation, and cache operations.
- [Incident Response Guide](docs/runbooks/INCIDENT_RESPONSE.md) — Severity classifications, mitigation playbooks, and post-incident review templates.
- [Backup & Recovery Guide](docs/runbooks/BACKUP_RECOVERY.md) — RPO/RTO objectives, manifest format, and restore procedures.
- [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md) — Deployment instructions for Docker Compose, Kubernetes, Railway, and Vercel.

---

## Scope Boundaries and Policies

This repository strictly implements **Phases 1 through 16**. The following capabilities are explicitly omitted by architectural policy:

- Automated Final Submissions or Headless Browser Submissions: Candidate review and explicit human submission confirmation are mandatory to guarantee application truthfulness and protect candidate reputations.
- Payment Processing & Billing: Third-party billing or Stripe subscription mechanics are intentionally excluded to keep the codebase pure and infrastructure-focused.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.
