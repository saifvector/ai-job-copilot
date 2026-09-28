# System Architecture — AI Job Copilot (Phase 1)

## Overview

**AI Job Copilot** is designed following strict **Domain-Driven Design (DDD)** and **Clean Architecture** principles. The application is structured as a modular monorepo cleanly isolating the presentation layer, domain and business service layer, persistence layer, and external infrastructure.

```
                    ┌────────────────────────────────────────┐
                    │      Next.js 15 Client Frontend        │
                    │   (App Router, Tailwind, Zustand)      │
                    └───────────────────┬────────────────────┘
                                        │ HTTP / JSON
                                        ▼
                    ┌────────────────────────────────────────┐
                    │     FastAPI Gateway & API Routers      │
                    │         (/api/v1/*, /health)           │
                    └───────────────────┬────────────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
              ┌─────────────────────┐       ┌─────────────────────┐
              │ Correlation & Trace │       │ Global Error Handler│
              │     Middleware      │       │     Middleware      │
              └──────────┬──────────┘       └──────────┬──────────┘
                         │                             │
                         ▼                             ▼
              ┌───────────────────────────────────────────────────┐
              │               Service Layer (Domain)              │
              │       (UserService, ProfileService, Base)         │
              └─────────────────────────┬─────────────────────────┘
                                        │
                                        ▼
              ┌───────────────────────────────────────────────────┐
              │             Repository Layer (Data Access)        │
              │     (UserRepository, ProfileRepository, Base)     │
              └─────────────────────────┬─────────────────────────┘
                                        │
                                        ▼
              ┌───────────────────────────────────────────────────┐
              │              Database Persistence                 │
              │         (PostgreSQL + Prisma ORM + asyncpg)       │
              └───────────────────────────────────────────────────┘
```

---

## Architecture Layers

### 1. Presentation Layer (`frontend/`)
* **Framework**: Next.js 15 (App Router with React 19).
* **Styling**: Tailwind CSS configured with a semantic design token system (CSS variables supporting seamless dark/light modes).
* **Component Library**: Custom accessible design system built on top of shadcn/ui patterns (`Button`, `Input`, `Select`, `Card`, `Modal`, `Table`, `Badge`, `Loader`, `Empty State`).
* **State Management**: Zustand stores (`useUserStore`, `useUIStore`) for predictable client-side UI and session state.
* **API Client**: Abstraction layer with custom timeout handling, standard error normalization, and environment-driven base URL configuration.

### 2. API Gateway & Middleware (`backend/api/`, `backend/middleware/`)
* **API Versioning**: URL-prefix versioning (`/api/v1`) with independent sub-routers.
* **Correlation ID**: Generates or propagates incoming `X-Correlation-ID` through `contextvars` to all logs and error responses.
* **Request Timing**: Records exact processing latency and injects `X-Process-Time`.
* **Centralized Exception Handling**: Traps domain exceptions, Pydantic validation errors, and database exceptions, formatting them into standard JSON envelopes.

### 3. Domain & Service Layer (`backend/services/`)
* Contains pure business rules without coupling to HTTP request/response objects.
* Implements `BaseService[Model, CreateSchema, UpdateSchema]` for generic CRUD logic.
* Validates unique constraints, business state transitions, and orchestrates cross-repository actions.

### 4. Data Access Layer (`backend/repositories/`)
* Encapsulates all query formulation using async SQLAlchemy 2.0.
* Implements `BaseRepository[Model]` providing typed methods: `get_by_id`, `list`, `count`, `create`, `update`, `delete`.
* Injected into services via FastAPI Dependency Injection (`Depends`).

### 5. Database Layer (`database/`)
* Single source of truth schema defined in `database/prisma/schema.prisma`.
* Migration SQL generated and tracked in version control.
* PostgreSQL 16 database with UUID v4 primary keys, composite indices, and cascading foreign keys.
