from fastapi import APIRouter
from api.v1.endpoints import (
    health,
    jobs,
    matching,
    profile_intelligence,
    profiles,
    resume,
    users,
    dashboard,
    resume_tailoring,
    applications,
    reports,
    recruiters,
    referrals,
    interview,
    application_assistant,
    auth,
    audit_logs,
    system,
    webhooks,
    developer,
    agents,
    tasks,
    workflows,
    intelligence,
)

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(health.router, tags=["Health & Diagnostics"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_v1_router.include_router(profile_intelligence.router, prefix="/profile", tags=["Profile Intelligence"])
api_v1_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_v1_router.include_router(resume_tailoring.router, prefix="/resume", tags=["Resume Tailoring"])
api_v1_router.include_router(jobs.router, prefix="/jobs", tags=["Job Discovery"])
api_v1_router.include_router(matching.router, prefix="/matching", tags=["Job Matching Engine"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard & Analytics"])
api_v1_router.include_router(applications.router, prefix="/applications", tags=["Application Tracking System"])
api_v1_router.include_router(reports.router, prefix="/reports", tags=["Reporting & Export Center"])
api_v1_router.include_router(recruiters.router, prefix="/recruiters", tags=["Recruiter CRM & Networking"])
api_v1_router.include_router(referrals.router, prefix="/referrals", tags=["Referral Tracking"])
api_v1_router.include_router(interview.router, prefix="/interview", tags=["AI Interview Preparation"])
api_v1_router.include_router(application_assistant.router, prefix="/application-assistant", tags=["Application Assistant"])
api_v1_router.include_router(auth.router, tags=["Security & Authentication"])
api_v1_router.include_router(audit_logs.router, tags=["Audit Logging & Compliance"])
api_v1_router.include_router(system.router, tags=["System Operations & Observability"])
api_v1_router.include_router(webhooks.router, tags=["Webhooks & Event Subscriptions"])
api_v1_router.include_router(developer.router, tags=["Developer Portal & Platform"])
api_v1_router.include_router(agents.router, tags=["AI Agents & Registry"])
api_v1_router.include_router(tasks.router, tags=["Agent Tasks & Background Execution"])
api_v1_router.include_router(workflows.router, tags=["Multi-Agent Workflow Engine"])
api_v1_router.include_router(intelligence.router, tags=["Career Intelligence & Outcome Learning"])



