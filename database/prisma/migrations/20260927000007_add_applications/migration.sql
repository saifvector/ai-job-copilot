-- Migration: 20260927000007_add_applications
-- Description: Creates applications, application_events, and interviews tables for Phase 8 Application Tracking System

-- CreateTable: applications
CREATE TABLE IF NOT EXISTS "applications" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "job_id" UUID NOT NULL,
    "tailored_resume_id" UUID,
    "status" VARCHAR(50) NOT NULL DEFAULT 'SAVED',
    "application_date" TIMESTAMPTZ(6),
    "last_updated" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "source" VARCHAR(100),
    "notes" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_applications" PRIMARY KEY ("id"),
    CONSTRAINT "uq_applications_user_job" UNIQUE ("user_id", "job_id"),
    CONSTRAINT "fk_applications_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_applications_job" FOREIGN KEY ("job_id") REFERENCES "jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_applications_tailored_resume" FOREIGN KEY ("tailored_resume_id") REFERENCES "tailored_resumes"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateIndexes for applications
CREATE INDEX IF NOT EXISTS "idx_applications_user_id" ON "applications"("user_id");
CREATE INDEX IF NOT EXISTS "idx_applications_job_id" ON "applications"("job_id");
CREATE INDEX IF NOT EXISTS "idx_applications_status" ON "applications"("status");
CREATE INDEX IF NOT EXISTS "idx_applications_user_status" ON "applications"("user_id", "status");

-- CreateTable: application_events
CREATE TABLE IF NOT EXISTS "application_events" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "application_id" UUID NOT NULL,
    "event_type" VARCHAR(100) NOT NULL,
    "description" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_application_events" PRIMARY KEY ("id"),
    CONSTRAINT "fk_application_events_application" FOREIGN KEY ("application_id") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndexes for application_events
CREATE INDEX IF NOT EXISTS "idx_application_events_application_id" ON "application_events"("application_id");
CREATE INDEX IF NOT EXISTS "idx_application_events_created_at" ON "application_events"("created_at");

-- CreateTable: interviews
CREATE TABLE IF NOT EXISTS "interviews" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "application_id" UUID NOT NULL,
    "interview_type" VARCHAR(50) NOT NULL,
    "interview_date" TIMESTAMPTZ(6) NOT NULL,
    "interview_round" INTEGER NOT NULL DEFAULT 1,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_interviews" PRIMARY KEY ("id"),
    CONSTRAINT "fk_interviews_application" FOREIGN KEY ("application_id") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndexes for interviews
CREATE INDEX IF NOT EXISTS "idx_interviews_application_id" ON "interviews"("application_id");
CREATE INDEX IF NOT EXISTS "idx_interviews_interview_date" ON "interviews"("interview_date");
