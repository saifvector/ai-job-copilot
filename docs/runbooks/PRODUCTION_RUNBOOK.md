# AI Job Copilot - Production Runbook

## 1. System Overview

AI Job Copilot is a production-grade career automation and application intelligence SaaS.
The backend is powered by FastAPI (Python 3.13), backed by PostgreSQL (managed via Prisma / SQLAlchemy), Redis 7 (caching and Celery broker), and background task workers. The frontend is built on Next.js 15 and deployed on Vercel or containerized Kubernetes/Docker environments.

---

## 2. Core Service Topology & Ports

| Service | Port | Description | Health Endpoint |
|---|---|---|---|
| **API Server (FastAPI)** | `8000` | Core REST APIs, auth, intelligence orchestration | `GET /health` (or `GET /health?detailed=true`) |
| **Worker (Celery / Async Runner)** | N/A | Asynchronous queues (`sync_jobs`, `matching`, `reports`) | Process heartbeat / Redis ping |
| **PostgreSQL Database** | `5432` | Relational store for users, resumes, jobs, applications, audit logs | `SELECT 1;` / `GET /health/database` |
| **Redis Cache & Broker** | `6379` | Response caching, sliding window rate limits, job broker | `PING` / `GET /health/cache` |
| **Next.js Web Client** | `3000` | React UI, SSR, and client stores | `GET /` |

---

## 3. Standard Operating Procedures (SOPs)

### 3.1 Service Start & Stop Procedures

#### Local / Docker Compose
- **Start All Services**:
  ```bash
  docker compose -f docker-compose.prod.yml up -d
  ```
- **View Aggregated Logs**:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f --tail=100
  ```
- **Graceful Shutdown**:
  ```bash
  docker compose -f docker-compose.prod.yml down --timeout 30
  ```

#### Kubernetes Cluster
- **Deploy/Rollout Update**:
  ```bash
  kubectl apply -k k8s/
  kubectl rollout restart deployment/backend-api -n ai-job-copilot
  kubectl rollout status deployment/backend-api -n ai-job-copilot
  ```
- **Drain Worker Nodes Before Maintenance**:
  ```bash
  kubectl scale deployment/backend-worker --replicas=0 -n ai-job-copilot
  ```

---

### 3.2 Secret Key & Credential Rotation

AI Job Copilot supports zero-downtime secret key rotation for JWT tokens via `SecretKeyManager`:

1. **Generate New Secret**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
2. **Apply Rotated Configuration**:
   - Set `PREVIOUS_SECRET_KEY` = `<current_secret_key>`.
   - Set `SECRET_KEY` = `<new_generated_key>`.
   - New tokens are signed with the new primary key.
   - Active tokens signed with the previous key continue to validate gracefully during the transition grace period.
3. **Decommission Old Secret**:
   - Once all active sessions have rotated or expired (typically after `ACCESS_TOKEN_EXPIRE_MINUTES` + `REFRESH_TOKEN_EXPIRE_DAYS`), remove `PREVIOUS_SECRET_KEY`.

---

### 3.3 Database Maintenance & Connection Pool Tuning

- **Pool Configuration Defaults**:
  - `POOL_SIZE`: 10 connections per worker process.
  - `MAX_OVERFLOW`: 20 connections for burst traffic.
  - `POOL_TIMEOUT`: 30 seconds wait timeout.
  - `POOL_RECYCLE`: 1800 seconds (30 minutes) to prevent stale connections.
- **Checking Active Connections & Health**:
  ```bash
  curl -s http://localhost:8000/health/database | jq .
  ```
- **Checking Pool Saturation**:
  Query the `/metrics` endpoint to monitor `db_pool_size`, `db_pool_checked_out`, and `db_pool_overflow`.

---

### 3.4 Redis Caching & Invalidation Procedures

The application caches computationally expensive lookups across three primary namespaces:
- `jobs:search:*` (TTL: 300s)
- `matches:user:*` (TTL: 600s)
- `analytics:user:*` (TTL: 900s)

#### Manual Invalidation
- **Purge all job search cache**:
  ```bash
  redis-cli --scan --pattern "jobs:search:*" | xargs -r redis-cli del
  ```
- **Purge a specific user's match cache**:
  ```bash
  redis-cli del "matches:user:<user_id>"
  ```
- **Flush Entire Cache (Emergency Only)**:
  ```bash
  redis-cli flushdb async
  ```

---

### 3.5 Background Queue Management

Queues:
1. `sync_jobs_queue`: Scheduled or on-demand external job board ingestion.
2. `matching_queue`: Heavy multi-dimensional candidate-to-job matching computations.
3. `reports_queue`: Asynchronous PDF/CSV aggregation and export generation.

- **Check Task Status via API**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/system/tasks/<task_id> \
       -H "Authorization: Bearer <admin_token>"
  ```
- **Run Standalone Worker**:
  ```bash
  python -m backend.workers.task_worker
  ```

---

## 4. Health Checks & Observability Matrix

| Metric / Endpoint | Normal Range | Alert Threshold | Action Required |
|---|---|---|---|
| `GET /health` | `status: "healthy"` | Any `degraded` or `unhealthy` | Inspect subsystem status breakdowns |
| `API p95 Latency` | `< 300ms` | `> 750ms` | Check DB slow queries, Redis latency, AI timeouts |
| `Error Rate (5xx)` | `< 0.1%` | `> 1.0%` | Inspect logs for unhandled exceptions or upstream outages |
| `AI Token Budget` | Within monthly allocation | `> 85%` quota | Notify billing, switch to Gemini 2.5 Flash fallback |
| `DB Connection Pool` | `< 70%` checked out | `> 90%` | Scale read replicas or increase `MAX_OVERFLOW` |

---

## 5. Security Checklists

- [x] All tokens signed with high-entropy cryptographic secrets (256-bit+).
- [x] Refresh token reuse triggers immediate family-wide revocation.
- [x] Sliding-window rate limiter active on all public and authenticated endpoints.
- [x] MIME magic-byte verification strictly enforced on resume file uploads.
- [x] Suspicious or infected uploads isolated to quarantine storage (`./storage/quarantine`).
- [x] Double-submit CSRF cookie checks active for cookie-authenticated browser clients.
- [x] Audit log tracks all security-sensitive user actions (`resume_upload`, `profile_update`, `report_generate`, `application_create`).
