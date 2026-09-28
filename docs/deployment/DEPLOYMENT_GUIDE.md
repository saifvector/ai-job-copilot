# AI Job Copilot - Production Deployment Guide

## 1. Supported Deployment Environments

AI Job Copilot is engineered with a modular, 12-factor cloud-native architecture supporting four primary production targets:

1. **Docker Compose**: Single-node turnkey production deployment with Postgres, Redis, API, Celery Worker, and Next.js frontend.
2. **Kubernetes (K8s)**: Horizontally autoscaled multi-node enterprise cluster with Ingress, TLS, HPA, ConfigMaps, and Secrets.
3. **Railway**: Managed containerized PaaS for backend API and background workers.
4. **Vercel**: Edge-optimized serverless hosting for Next.js frontend with security headers.

---

## 2. Environment Variables & Secret Configuration

Create a `.env.production` file with the following variables:

```bash
# Application Environment
ENVIRONMENT=production
DEBUG=false
APP_VERSION=1.0.0
CORS_ORIGINS=["https://app.jobcopilot.io","https://jobcopilot.io"]

# Authentication & Security
SECRET_KEY=replace_with_a_64_character_cryptographically_secure_random_string
PREVIOUS_SECRET_KEY=optional_previous_key_for_zero_downtime_rotation
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
CSRF_ENABLED=true
RATE_LIMITING_ENABLED=true

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://copilot_user:secure_password@postgres:5432/job_copilot_prod
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Caching & Background Queues (Redis)
REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_ENABLED=true

# AI Provider (Google Gemini)
GEMINI_API_KEY=AIzaSyYourProductionGeminiApiKey
GEMINI_MODEL=gemini-2.5-pro

# Storage & Backups
UPLOAD_DIR=/var/data/uploads
QUARANTINE_DIR=/var/data/quarantine
BACKUP_DIR=/var/data/backups
```

---

## 3. Option A: Production Docker Compose Deployment

The provided [docker-compose.prod.yml](file:///c:/Users/saifu/Desktop/Job%20applier/docker-compose.prod.yml) orchestrates 5 isolated containers with resource limits and health probes.

### Step 1: Provision Environment
```bash
cp .env.example .env.production
# Fill in real production secrets
```

### Step 2: Build and Launch
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Step 3: Run Database Migrations
```bash
docker compose -f docker-compose.prod.yml exec backend npx prisma migrate deploy
```

### Step 4: Verify Health
```bash
docker compose -f docker-compose.prod.yml ps
curl -s http://localhost:8000/health | jq .
```

---

## 4. Option B: Kubernetes (K8s) Cluster Deployment

All manifests are organized under the [`k8s/`](file:///c:/Users/saifu/Desktop/Job%20applier/k8s) directory:
- `namespace.yaml`
- `configmap.yaml`
- `secrets.yaml`
- `redis.yaml`
- `backend-deployment.yaml`
- `worker-deployment.yaml`
- `frontend-deployment.yaml`
- `ingress.yaml`
- `hpa.yaml`

### Step 1: Create Namespace and Configs
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
```

### Step 2: Deploy Redis & Core Services
```bash
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Step 3: Deploy Ingress & Autoscaler
```bash
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

### Step 4: Monitor Pods and HPA
```bash
kubectl get pods -n ai-job-copilot
kubectl get hpa -n ai-job-copilot
```

---

## 5. Option C: Railway (PaaS) Backend Deployment

The repository includes a root [railway.toml](file:///c:/Users/saifu/Desktop/Job%20applier/railway.toml) and [Procfile](file:///c:/Users/saifu/Desktop/Job%20applier/Procfile).

1. Connect your GitHub repository to Railway.
2. Add a **PostgreSQL** and a **Redis** plugin in the Railway project dashboard.
3. Configure the Railway Web Service:
   - Root Directory: `/`
   - Build Command: `pip install -r backend/requirements.txt && cd database && npx prisma generate`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 4`
4. Configure the Railway Worker Service:
   - Start Command: `python -m backend.workers.task_worker`
5. Supply environment variables mapped from the database/redis plugins.

---

## 6. Option D: Vercel Frontend Deployment

The Next.js client includes [frontend/vercel.json](file:///c:/Users/saifu/Desktop/Job%20applier/frontend/vercel.json) with security headers preconfigured (`X-Content-Type-Options`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Content-Security-Policy`).

1. Import repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. Set **Framework Preset** to `Next.js`.
4. Configure Environment Variables:
   - `NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1`
5. Deploy.

---

## 7. Post-Deployment Verification & Smoke Tests

Run these checks against your production deployment domain:

1. **Root Health Check**:
   ```bash
   curl -I https://api.yourdomain.com/health
   # Expected: HTTP/2 200 OK, {"status":"healthy"}
   ```
2. **Deep Component Diagnostics**:
   ```bash
   curl -s https://api.yourdomain.com/health?detailed=true | jq .
   # Verify database.status == "healthy" and cache.status == "healthy"
   ```
3. **Prometheus Telemetry Scrape**:
   ```bash
   curl -s https://api.yourdomain.com/metrics | grep "job_copilot_"
   ```
4. **Rate Limit Assertion**:
   ```bash
   # Send burst requests to verify 429 response after threshold
   for i in {1..35}; do curl -s -o /dev/null -w "%{http_code}\n" https://api.yourdomain.com/api/v1/jobs/search; done
   ```
