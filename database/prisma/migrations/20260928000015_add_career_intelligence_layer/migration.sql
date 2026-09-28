-- Migration: 20260928000015_add_career_intelligence_layer
-- Description: Phase 16 - Career Intelligence and Outcome Learning Platform, Outcome Events, Resume Performance, Skill Impact, and Historical Warehouse Snapshots

-- CreateTable: outcome_events
CREATE TABLE IF NOT EXISTS "outcome_events" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "application_id" UUID NOT NULL,
    "outcome_type" VARCHAR(50) NOT NULL,
    "occurred_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "notes" TEXT,
    "metadata" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "outcome_events_pkey" PRIMARY KEY ("id")
);

-- CreateTable: resume_performances
CREATE TABLE IF NOT EXISTS "resume_performances" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "tailored_resume_id" UUID,
    "applications_sent" INTEGER NOT NULL DEFAULT 0,
    "interviews_received" INTEGER NOT NULL DEFAULT 0,
    "offers_received" INTEGER NOT NULL DEFAULT 0,
    "response_rate" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "resume_performances_pkey" PRIMARY KEY ("id")
);

-- CreateTable: skill_impacts
CREATE TABLE IF NOT EXISTS "skill_impacts" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "skill_name" VARCHAR(100) NOT NULL,
    "interviews_influenced" INTEGER NOT NULL DEFAULT 0,
    "offers_influenced" INTEGER NOT NULL DEFAULT 0,
    "average_match_score" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "skill_impacts_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "uq_skill_impacts_user_skill" UNIQUE ("user_id", "skill_name")
);

-- CreateTable: career_intelligence_snapshots
CREATE TABLE IF NOT EXISTS "career_intelligence_snapshots" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "snapshot_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "total_applications" INTEGER NOT NULL DEFAULT 0,
    "interview_rate" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "offer_rate" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "rejection_rate" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "average_response_days" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "metrics_payload" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "career_intelligence_snapshots_pkey" PRIMARY KEY ("id")
);

-- CreateIndexes
CREATE INDEX IF NOT EXISTS "idx_outcome_events_user_id" ON "outcome_events"("user_id");
CREATE INDEX IF NOT EXISTS "idx_outcome_events_application_id" ON "outcome_events"("application_id");
CREATE INDEX IF NOT EXISTS "idx_outcome_events_type" ON "outcome_events"("outcome_type");
CREATE INDEX IF NOT EXISTS "idx_outcome_events_occurred_at" ON "outcome_events"("occurred_at");

CREATE INDEX IF NOT EXISTS "idx_resume_performances_user_id" ON "resume_performances"("user_id");
CREATE INDEX IF NOT EXISTS "idx_resume_performances_resume_id" ON "resume_performances"("tailored_resume_id");
CREATE INDEX IF NOT EXISTS "idx_resume_performances_response_rate" ON "resume_performances"("response_rate");

CREATE INDEX IF NOT EXISTS "idx_skill_impacts_user_id" ON "skill_impacts"("user_id");
CREATE INDEX IF NOT EXISTS "idx_skill_impacts_skill_name" ON "skill_impacts"("skill_name");
CREATE INDEX IF NOT EXISTS "idx_skill_impacts_interviews" ON "skill_impacts"("interviews_influenced");

CREATE INDEX IF NOT EXISTS "idx_career_snapshots_user_id" ON "career_intelligence_snapshots"("user_id");
CREATE INDEX IF NOT EXISTS "idx_career_snapshots_date" ON "career_intelligence_snapshots"("snapshot_date");

-- AddForeignKeys
ALTER TABLE "outcome_events" DROP CONSTRAINT IF EXISTS "outcome_events_user_id_fkey";
ALTER TABLE "outcome_events" ADD CONSTRAINT "outcome_events_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "outcome_events" DROP CONSTRAINT IF EXISTS "outcome_events_application_id_fkey";
ALTER TABLE "outcome_events" ADD CONSTRAINT "outcome_events_application_id_fkey" FOREIGN KEY ("application_id") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "resume_performances" DROP CONSTRAINT IF EXISTS "resume_performances_user_id_fkey";
ALTER TABLE "resume_performances" ADD CONSTRAINT "resume_performances_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "resume_performances" DROP CONSTRAINT IF EXISTS "resume_performances_tailored_resume_id_fkey";
ALTER TABLE "resume_performances" ADD CONSTRAINT "resume_performances_tailored_resume_id_fkey" FOREIGN KEY ("tailored_resume_id") REFERENCES "tailored_resumes"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "skill_impacts" DROP CONSTRAINT IF EXISTS "skill_impacts_user_id_fkey";
ALTER TABLE "skill_impacts" ADD CONSTRAINT "skill_impacts_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "career_intelligence_snapshots" DROP CONSTRAINT IF EXISTS "career_intelligence_snapshots_user_id_fkey";
ALTER TABLE "career_intelligence_snapshots" ADD CONSTRAINT "career_intelligence_snapshots_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
