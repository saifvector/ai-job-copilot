# AI Job Copilot - Developer Platform Documentation

Welcome to the **AI Job Copilot Developer Platform**. Phase 14 transforms AI Job Copilot into an extensible enterprise platform, allowing third-party services, applicant tracking systems (ATS), custom workflows, analytics tools, and ecosystem partners to programmatically interact with candidate data, matches, applications, and reports.

---

## Table of Contents
1. [Platform Architecture Overview](#platform-architecture-overview)
2. [Authentication & API Keys](#authentication--api-keys)
3. [Rate Limiting & Usage Quotas](#rate-limiting--usage-quotas)
4. [Public API v1](#public-api-v1)
5. [Webhook Delivery Engine](#webhook-delivery-engine)
6. [Integration Framework](#integration-framework)
7. [Plugin SDK](#plugin-sdk)
8. [Telemetry & API Analytics](#telemetry--api-analytics)
9. [Security & Best Practices](#security--best-practices)

---

## 1. Platform Architecture Overview

The AI Job Copilot platform is architected around 4 decoupled layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Third-Party Ecosystem                           │
│   (ATS Platforms, Zapier, Custom Dashboards, CLI Tools, Mobile Apps)   │
└───────────────▲──────────────────────────┬─────────────────────────────┘
                │ HTTP Requests            │ Outbound Webhooks
                │ (X-API-Key: ajc_live_*)  │ (HMAC-SHA256 signature)
┌───────────────┴──────────────────────────▼─────────────────────────────┐
│                      Public API Layer (/api/public/v1/*)               │
│  - Profile      - Resumes      - AI Matches   - Applications  - Reports│
│  - Scope Enforcement  - Sliding Window Limiter  - Telemetry Logger     │
└────────────────────────────────────────────────────────────────────────┘
                │                          │
┌───────────────▼──────────────────────────▼─────────────────────────────┐
│                       Integration Framework Layer                      │
│  - Email Providers: GmailProvider, OutlookProvider                     │
│  - Calendar Providers: GoogleCalendarProvider, OutlookCalendarProvider │
│  - Storage Providers: GoogleDriveProvider, DropboxProvider, OneDrive   │
│  - Team Notifications: SlackProvider                                   │
└────────────────────────────────────────────────────────────────────────┘
                │                          │
┌───────────────▼──────────────────────────▼─────────────────────────────┐
│                        Plugin SDK Architecture                         │
│  - BasePlugin Lifecycle  - PluginManifest  - PluginRegistry Singleton │
│  - Extension Hooks: on_custom_job_provider, on_custom_analytics, etc.  │
│  - Reference Plugins: NotionExport, GitHubJobs, CandidateDiversity     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication & API Keys

All calls to the Versioned Public API (`/api/public/v1/*`) require an active API key passed in the `X-API-Key` HTTP header.

### Key Format & Security
- **Prefix**: `ajc_live_` followed by an 8-character random prefix identifier.
- **Secret Token**: High-entropy 32-byte cryptographically secure random token (`secrets.token_urlsafe(32)`).
- **Storage**: Plaintext secrets are never stored in the database. Only the SHA-256 hash (`hashlib.sha256(raw_key.encode()).hexdigest()`) is persisted.
- **Rotation**: Keys can be rotated on demand via `POST /api/v1/developer/keys/{id}/rotate`, issuing a new secret while preserving name and granted scopes.

### Scopes & Permissions
API keys enforce granular least-privilege permission scopes:
| Scope | Description | Allowed Operations |
|---|---|---|
| `read:profile` | Read profile | Access candidate bio, preferred roles, target locations, experience years |
| `read:resume` | Read resumes | Access parsed resumes, normalized skills, certifications, work history |
| `read:matches` | Read match results | Query AI job matches, match scores, strengths, and recommendations |
| `read:applications` | Read applications | Inspect candidate pipeline status, interview stages, and notes |
| `write:applications` | Create applications | Programmatically log applications and trigger real-time dispatch |
| `read:reports` | Read reports | Query generated career documents, PDF metrics, and export history |

---

## 3. Rate Limiting & Usage Quotas

Every incoming public request is evaluated against:
1. **Sliding-Window Rate Limiter**: Default `60 requests per minute` per API key (customizable up to 1,000 req/min).
2. **Monthly Usage Quota**: Enforces a monthly limit (default `10,000 calls/month`). When exceeded, requests receive `HTTP 429 Too Many Requests`.
3. **Response Headers**:
   - `X-RateLimit-Limit`: Maximum requests permitted per minute.
   - `X-RateLimit-Remaining`: Remaining request allowance in current sliding window.

---

## 4. Public API v1 Base

Base URL: `http://localhost:8000/api/public/v1`

See [API Reference](API_REFERENCE.md) for full endpoint specifications, query parameters, and JSON schemas.

---

## 5. Webhook Delivery Engine

The outbound webhook system enables automated, event-driven integrations.

### Supported Events
- `resume.parsed`: Emitted when a new resume is analyzed and indexed.
- `job.matched`: Emitted when a job match score exceeds threshold.
- `report.generated`: Emitted when a PDF/JSON analytics report finishes generating.
- `application.created`: Emitted when a candidate submits an application.
- `application.updated`: Emitted when an application status or interview stage changes.

### Delivery Verification (HMAC-SHA256)
All webhook payloads include the header:
```http
X-Webhook-Signature: t=1727521200,v1=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
X-Webhook-Event: application.created
```
See the [Webhook Guide](WEBHOOK_GUIDE.md) for complete verification implementations in Node.js, Python, and Go.

---

## 6. Integration Framework

The provider architecture is located in `backend/integrations/`:
- `IntegrationProvider`: Abstract base declaring `provider_id`, `category`, `connect()`, `disconnect()`, `sync()`, and `get_status()`.
- **Email Providers**:
  - `GmailProvider`: Scans recruiter correspondence, tracks inbound responses.
  - `OutlookProvider`: Parses Outlook/Office 365 recruitment messages.
- **Calendar Providers**:
  - `GoogleCalendarProvider`: Schedules interview blocks, sets event reminders.
  - `OutlookCalendarProvider`: Synchronizes Outlook calendars for scheduled interviews.
- **Cloud Storage Providers**:
  - `GoogleDriveProvider`: Exports resumes and reports to Google Drive folders.
  - `DropboxProvider`: Backs up candidate versions into Dropbox repositories.
  - `OneDriveProvider`: Stores tailored PDFs in Microsoft OneDrive.
- **Team Notifications**:
  - `SlackProvider`: Posts high-match job opportunities and interview notifications to designated Slack channels.

---

## 7. Plugin SDK

Developers can author modular plugins by extending `BasePlugin` and implementing declared hooks:
- `on_custom_job_provider`: Ingest external job listings.
- `on_custom_analytics`: Calculate specialized domain metrics.
- `on_custom_export`: Streamline exports into proprietary systems (e.g. Notion, Airtable).

See the [Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md) for full details.
