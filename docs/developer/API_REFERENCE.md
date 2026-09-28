# Public API Reference (v1)

Base URL:
`http://localhost:8000/api/public/v1`

All requests require the `X-API-Key` HTTP header.

---

## 1. Candidate Profile

### `GET /api/public/v1/profile`
Retrieve candidate profile information, career preferences, target roles, and target locations.

**Required Scope**: `read:profile`

#### Request
```bash
curl -X GET "http://localhost:8000/api/public/v1/profile" \
  -H "X-API-Key: ajc_live_sample_key_12345"
```

#### Response (200 OK)
```json
{
  "id": "a0000000-0000-0000-0000-000000000001",
  "name": "Alex Chen",
  "email": "alex.chen@example.com",
  "phone": "+1-555-0199",
  "preferred_roles": ["Staff Software Engineer", "Platform Architect"],
  "preferred_locations": ["Remote", "San Francisco, CA"],
  "years_of_experience": 8,
  "created_at": "2026-09-28T08:00:00Z",
  "updated_at": "2026-09-28T09:30:00Z"
}
```

---

## 2. Resumes

### `GET /api/public/v1/resumes`
List candidate parsed resumes and indexed skills.

**Required Scope**: `read:resume`

#### Request
```bash
curl -X GET "http://localhost:8000/api/public/v1/resumes?skip=0&limit=20" \
  -H "X-API-Key: ajc_live_sample_key_12345"
```

#### Response (200 OK)
```json
{
  "items": [
    {
      "id": "b1111111-1111-1111-1111-111111111111",
      "user_id": "a0000000-0000-0000-0000-000000000001",
      "file_name": "alex_chen_platform_lead.pdf",
      "content_type": "application/pdf",
      "skills_count": 24,
      "experience_years": 8.5,
      "parsed_skills": ["Python", "FastAPI", "PostgreSQL", "Kafka", "Docker", "Kubernetes"],
      "created_at": "2026-09-28T08:15:00Z"
    }
  ],
  "total": 1
}
```

---

## 3. Match Results

### `GET /api/public/v1/matches`
Query AI match evaluations between candidate qualifications and ingested job listings.

**Required Scope**: `read:matches`

#### Query Parameters
- `min_score` (optional, float): Minimum overall match score (e.g. `80.0`).
- `limit` (optional, integer): Maximum results returned (default `20`).
- `skip` (optional, integer): Pagination offset (default `0`).

#### Request
```bash
curl -X GET "http://localhost:8000/api/public/v1/matches?min_score=80&limit=10" \
  -H "X-API-Key: ajc_live_sample_key_12345"
```

#### Response (200 OK)
```json
{
  "items": [
    {
      "id": "c2222222-2222-2222-2222-222222222222",
      "job_id": "d3333333-3333-3333-3333-333333333333",
      "job_title": "Principal Platform Engineer",
      "company": "Stripe",
      "location": "Remote (US)",
      "overall_score": 94.5,
      "skill_score": 96.0,
      "experience_score": 93.0,
      "strengths": [
        "Extensive experience with high-throughput distributed APIs",
        "Direct proficiency in FastAPI and async database patterns"
      ],
      "missing_skills": ["gRPC"],
      "recommendations": [
        "Emphasize scalable multi-tenant architecture experience during initial screen"
      ],
      "apply_url": "https://stripe.com/jobs/principal-platform"
    }
  ],
  "total": 1
}
```

---

## 4. Applications

### `GET /api/public/v1/applications`
Retrieve the candidate's active application pipeline.

**Required Scope**: `read:applications`

#### Request
```bash
curl -X GET "http://localhost:8000/api/public/v1/applications" \
  -H "X-API-Key: ajc_live_sample_key_12345"
```

#### Response (200 OK)
```json
{
  "items": [
    {
      "id": "e4444444-4444-4444-4444-444444444444",
      "user_id": "a0000000-0000-0000-0000-000000000001",
      "job_id": "d3333333-3333-3333-3333-333333333333",
      "job_title": "Principal Platform Engineer",
      "company": "Stripe",
      "status": "Applied",
      "applied_at": "2026-09-28T09:45:00Z",
      "notes": "Submitted via automated partner workflow",
      "created_at": "2026-09-28T09:45:00Z",
      "updated_at": "2026-09-28T09:45:00Z"
    }
  ],
  "total": 1
}
```

### `POST /api/public/v1/applications`
Create a job application record programmatically and trigger `application.created` webhook notification.

**Required Scope**: `write:applications`

#### Request
```bash
curl -X POST "http://localhost:8000/api/public/v1/applications" \
  -H "X-API-Key: ajc_live_sample_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "d3333333-3333-3333-3333-333333333333",
    "status": "Applied",
    "notes": "Direct submission from ATS partner"
  }'
```

#### Response (201 Created)
```json
{
  "id": "e4444444-4444-4444-4444-444444444444",
  "user_id": "a0000000-0000-0000-0000-000000000001",
  "job_id": "d3333333-3333-3333-3333-333333333333",
  "job_title": "Principal Platform Engineer",
  "company": "Stripe",
  "status": "Applied",
  "applied_at": "2026-09-28T09:45:00Z",
  "notes": "Direct submission from ATS partner",
  "created_at": "2026-09-28T09:45:00Z",
  "updated_at": "2026-09-28T09:45:00Z"
}
```

---

## 5. Reports

### `GET /api/public/v1/reports`
List generated PDF and JSON analytical reports.

**Required Scope**: `read:reports`

#### Request
```bash
curl -X GET "http://localhost:8000/api/public/v1/reports" \
  -H "X-API-Key: ajc_live_sample_key_12345"
```

#### Response (200 OK)
```json
{
  "items": [
    {
      "id": "f5555555-5555-5555-5555-555555555555",
      "user_id": "a0000000-0000-0000-0000-000000000001",
      "title": "Comprehensive Career Readiness Audit",
      "report_type": "AUDIT",
      "format": "PDF",
      "file_size_bytes": 142050,
      "created_at": "2026-09-28T09:00:00Z"
    }
  ],
  "total": 1
}
```

---

## Standard Error Codes

| Status Code | Code | Reason |
|---|---|---|
| `401 Unauthorized` | `INVALID_API_KEY` | Missing, malformed, or revoked API key |
| `403 Forbidden` | `INSUFFICIENT_SCOPE` | Key lacks the required permission scope |
| `404 Not Found` | `RESOURCE_NOT_FOUND` | Specified Job or Resource ID does not exist |
| `429 Too Many Requests` | `RATE_LIMIT_EXCEEDED` | Exceeded rate limit or monthly usage limit |
| `500 Server Error` | `INTERNAL_ERROR` | Server execution exception |
