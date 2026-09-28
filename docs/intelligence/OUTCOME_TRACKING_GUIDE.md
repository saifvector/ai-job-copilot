# Outcome Tracking & Milestone Logging Guide

## 1. Overview

Outcome Tracking provides the raw telemetry required to train and refine candidate career intelligence. By logging hiring milestones promptly, candidates empower the platform to isolate which resume formulations, skills, and application channels produce interviews and offers.

---

## 2. Outcome Milestone Taxonomy

The platform records five standard outcome event types:

| Outcome Type | Description | State Impact | Key Metadata Attributes |
|---|---|---|---|
| `InterviewReceived` | Recruiter screen, hiring manager conversation, technical assessment loop, or onsite interview scheduled. | Updates application status to `INTERVIEW` | `round` (e.g. 1, 2, Final), `interviewer`, `format` |
| `AssessmentReceived` | Automated coding challenge, HackerRank, async video screening, or take-home assignment. | Updates application status to `ASSESSMENT` | `platform`, `duration_hours`, `due_date` |
| `OfferReceived` | Formal written employment offer extended by company. | Updates application status to `OFFER` | `offerAmount` (base salary), `equity`, `deadline` |
| `Rejected` | Application screened out or candidate not selected following an interview round. | Updates application status to `REJECTED` | `rejection_stage`, `feedback_notes` |
| `Withdrawn` | Candidate voluntarily withdrew application due to competing offer, role mismatch, or compensation misalignment. | Updates application status to `WITHDRAWN` | `withdrawal_reason` |

---

## 3. How to Record Outcomes

### 3.1 Via the Interactive Web UI
1. Navigate to `/intelligence` or `/applications`.
2. Click the **Record Outcome** button in the header.
3. Select the target application from your active pipeline dropdown.
4. Select the outcome milestone (e.g., `Interview Received` or `Offer Received`).
5. Specify the event date and any pertinent context (e.g. interview round or salary offer).
6. Click **Record Outcome**. The application status and intelligence metrics update immediately.

### 3.2 Via the REST API
Send an authenticated HTTP POST request to `/api/v1/intelligence/outcomes`:

```http
POST /api/v1/intelligence/outcomes HTTP/1.1
Host: api.jobcopilot.local
Authorization: Bearer <JWT_OR_API_KEY>
Content-Type: application/json

{
  "application_id": "4a7b9c1d-3e5f-4a8b-9c1d-3e5f4a8b9c1d",
  "outcome_type": "InterviewReceived",
  "occurred_at": "2026-09-28T14:30:00Z",
  "notes": "Recruiter screen with Engineering Talent Lead; scheduled for 45 minutes",
  "metadata": {
    "round": 1,
    "format": "Google Meet",
    "technical_focus": "System Architecture & Python"
  }
}
```

Response (`201 Created`):
```json
{
  "id": "8f3e2a1b-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
  "user_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "application_id": "4a7b9c1d-3e5f-4a8b-9c1d-3e5f4a8b9c1d",
  "outcome_type": "InterviewReceived",
  "occurred_at": "2026-09-28T14:30:00Z",
  "notes": "Recruiter screen with Engineering Talent Lead; scheduled for 45 minutes",
  "metadata": {
    "round": 1,
    "format": "Google Meet",
    "technical_focus": "System Architecture & Python"
  },
  "created_at": "2026-09-28T14:30:15Z",
  "job_title": "Staff AI Engineer",
  "company": "Anthropic AI"
}
```

---

## 4. Automatic Downstream Pipeline Updates

When an outcome event is recorded:
1. The corresponding `ApplicationModel` status is updated (`INTERVIEW`, `OFFER`, `REJECTED`, etc.).
2. The `resume_performances` record for the tailored resume linked to the application is recalculated.
3. The `skill_impacts` table updates the interview/offer counts for every skill associated with the target job.
4. Downstream recommendations in the `CareerRecommendationEngine` recalibrate in real time.
