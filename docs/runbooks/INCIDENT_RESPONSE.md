# AI Job Copilot - Incident Response Guide

## 1. Severity Classifications & SLAs

| Severity | Definition | Target Acknowledgment | Target Resolution | Escalation Contact |
|---|---|---|---|---|
| **SEV-1 (Critical)** | Core service unavailable (Total API failure, database down, data corruption, auth breach). | < 5 minutes | < 1 hour | On-Call Lead + DevOps Architect |
| **SEV-2 (Major)** | Major functionality impaired (AI matching engine down, background queues stalled, high latency > 2s). | < 15 minutes | < 4 hours | Backend Lead |
| **SEV-3 (Moderate)** | Non-critical feature failure (Reporting PDF exports failing, cache miss fallbacks degraded). | < 1 hour | < 24 hours | Assigned Engineer |
| **SEV-4 (Minor)** | Minor UI cosmetic glitch, non-blocking telemetry delay, low-volume false positive warnings. | < 4 hours | Next Sprint | Bug Backlog |

---

## 2. Incident Response Workflow

```
[ALERT / DETECTION] ──> [TRIAGE & SEVERITY TAG] ──> [CONTAINMENT & MITIGATION]
                                                               │
[POST-MORTEM & ACTION ITEMS] <── [VERIFICATION] <── [ROOT CAUSE ERADICATION]
```

1. **Detection & Declaration**: Alert fired via Prometheus/Datadog or reported by user. Declare incident in `#incident-war-room`.
2. **Triage**: Assign Incident Commander (IC). Verify `/health` endpoints and structured logs.
3. **Containment**: Prioritize customer data safety and platform availability over deep debugging. Deploy fallbacks, bypass failing upstream services, or rotate compromised secrets.
4. **Eradication & Recovery**: Deploy hotfix or restore known good state from validated backup.
5. **Post-Mortem**: Document root cause, timeline, impact, and action items within 48 hours.

---

## 3. Incident Playbooks

### Playbook 1: API 500 Spike / Cascading Database Connection Exhaustion

**Symptoms**:
- HTTP 500 errors spike above 1%.
- Logs contain `sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 20 reached`.

**Mitigation Steps**:
1. Check database server CPU, RAM, and active connections:
   ```bash
   curl -s http://localhost:8000/health/database | jq .
   ```
2. Identify and terminate long-running idle transactions in PostgreSQL:
   ```sql
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE (now() - pg_stat_activity.query_start) > interval '2 minutes'
     AND state != 'idle';

   SELECT pg_terminate_backend(<pid>);
   ```
3. Restart or horizontally scale backend API pods to reset connection pools:
   ```bash
   kubectl rollout restart deployment/backend-api -n ai-job-copilot
   ```

---

### Playbook 2: Redis Outage / Cache Connection Failure

**Symptoms**:
- `GET /health/cache` reports `status: "degraded"` or `status: "unhealthy"`.
- Warning logs: `Redis unavailable, falling back to in-memory cache`.

**Mitigation Steps**:
1. Verify Redis pod/service status:
   ```bash
   kubectl get pods -l app=redis -n ai-job-copilot
   ```
2. Note: The application automatically degrades to `InMemoryCache` with zero user-facing downtime.
3. Restart Redis instance if unresponsive:
   ```bash
   kubectl rollout restart deployment/redis -n ai-job-copilot
   ```
4. Verify reconnect in backend logs:
   ```bash
   kubectl logs -l app=backend-api -n ai-job-copilot --tail=50 | grep -i "redis"
   ```

---

### Playbook 3: AI Provider Outage / Google Gemini Rate Limit (HTTP 429)

**Symptoms**:
- Tailoring, matching, or assistant endpoints return error category `AI Provider`.
- Error logs indicate `ResourceExhausted` or `QuotaExceeded`.

**Mitigation Steps**:
1. Check current token expenditure:
   ```bash
   curl -s -H "Authorization: Bearer <admin_token>" http://localhost:8000/api/v1/system/ai-costs | jq .
   ```
2. If quota is exceeded, switch model configuration from `gemini-2.5-pro` to `gemini-2.5-flash`:
   ```bash
   kubectl set env deployment/backend-api GEMINI_MODEL="gemini-2.5-flash" -n ai-job-copilot
   ```
3. Verify that the cache hit rate for recent job matches reduces redundant LLM queries:
   ```bash
   curl -s http://localhost:8000/health/cache | jq .
   ```

---

### Playbook 4: Suspected Token / Credential Compromise

**Symptoms**:
- User reports unauthorized activity or token leakage.
- Refresh token reuse alert logged: `Security Alert: Refresh token family reuse detected`.

**Mitigation Steps**:
1. Immediately revoke the token and its entire token family:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/revoke \
        -H "Content-Type: application/json" \
        -d '{"token": "<compromised_token>", "reason": "suspected_breach"}'
   ```
2. Review audit logs for affected user ID:
   ```bash
   curl -s "http://localhost:8000/api/v1/audit-logs?userId=<user_id>" \
        -H "Authorization: Bearer <admin_token>" | jq .
   ```
3. If systemic secret leak is suspected, execute the **Zero-Downtime Secret Rotation SOP** outlined in the Production Runbook.

---

### Playbook 5: Malicious File Upload / Malware Quarantine Alert

**Symptoms**:
- File validation endpoint blocks an upload with `is_quarantined: true` or `scan_verdict: "malicious"`.
- Warning alert logged: `Malware detected in upload`.

**Mitigation Steps**:
1. Confirm that the malicious file was quarantined in `./storage/quarantine` and was NOT ingested into user resumes.
2. Inspect the audit log for the offending user and client IP address:
   ```bash
   curl -s "http://localhost:8000/api/v1/audit-logs?action=resume_upload_blocked" \
        -H "Authorization: Bearer <admin_token>" | jq .
   ```
3. Block the IP address via the web firewall or update the sliding-window rate limiter blocklist.

---

## 4. Post-Incident Review (PIR) Template

- **Incident Date & Time**: `YYYY-MM-DD HH:MM UTC`
- **Severity**: `SEV-1 / SEV-2 / SEV-3 / SEV-4`
- **Incident Commander**: `[Name]`
- **Duration**: `X hours Y minutes`
- **Impact Summary**: Number of affected requests, users, or downtime percentage.
- **Root Cause Analysis (5 Whys)**:
  1. Why did the issue occur?
  2. Why did that happen?
  3. Why wasn't it caught earlier?
  4. Why did monitoring fail/succeed?
  5. What fundamental safeguard was missing?
- **Action Items & Preventative Measures**:
  - [ ] Add specific alert rule for condition
  - [ ] Expand integration/load test coverage
  - [ ] Update documentation or architecture safeguard
