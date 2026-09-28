-- Migration: 20260927000011_add_application_assistant
-- Phase 12: Application Assistant Platform

-- 1. Create application_drafts table
CREATE TABLE IF NOT EXISTS "application_drafts" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "job_id" UUID NOT NULL,
    "status" VARCHAR(50) NOT NULL DEFAULT 'Draft',
    "generated_answers" TEXT,
    "selected_resume_id" UUID,
    "readiness_score" DOUBLE PRECISION DEFAULT 0.0,
    "checklist" TEXT,
    "notes" TEXT,
    "submitted_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_application_drafts" PRIMARY KEY ("id"),
    CONSTRAINT "fk_application_drafts_user_id" FOREIGN KEY ("user_id") 
        REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_application_drafts_job_id" FOREIGN KEY ("job_id") 
        REFERENCES "jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_application_drafts_user_id" ON "application_drafts"("user_id");
CREATE INDEX IF NOT EXISTS "idx_application_drafts_job_id" ON "application_drafts"("job_id");
CREATE INDEX IF NOT EXISTS "idx_application_drafts_status" ON "application_drafts"("status");

-- 2. Create application_questions table
CREATE TABLE IF NOT EXISTS "application_questions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "draft_id" UUID NOT NULL,
    "question" TEXT NOT NULL,
    "generated_answer" TEXT,
    "user_answer" TEXT,
    "answer_type" VARCHAR(50) NOT NULL DEFAULT 'Text',
    "options" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "is_required" BOOLEAN NOT NULL DEFAULT true,
    "is_reviewed" BOOLEAN NOT NULL DEFAULT false,
    "order" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_application_questions" PRIMARY KEY ("id"),
    CONSTRAINT "fk_application_questions_draft_id" FOREIGN KEY ("draft_id") 
        REFERENCES "application_drafts"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_application_questions_draft_id" ON "application_questions"("draft_id");
CREATE INDEX IF NOT EXISTS "idx_application_questions_type" ON "application_questions"("answer_type");
