-- Migration: 20260927000004_add_matching_engine
-- Description: Creates match_results table for Phase 5 AI Job Matching Engine

-- CreateTable
CREATE TABLE IF NOT EXISTS "match_results" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "job_id" UUID NOT NULL,
    "overall_score" DECIMAL(5, 2) NOT NULL,
    "skill_score" DECIMAL(5, 2) NOT NULL,
    "experience_score" DECIMAL(5, 2) NOT NULL,
    "education_score" DECIMAL(5, 2) NOT NULL,
    "location_score" DECIMAL(5, 2) NOT NULL,
    "role_score" DECIMAL(5, 2) NOT NULL,
    "strengths" TEXT[] NOT NULL DEFAULT '{}',
    "missing_skills" TEXT[] NOT NULL DEFAULT '{}',
    "recommendations" TEXT[] NOT NULL DEFAULT '{}',
    "generated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_match_results" PRIMARY KEY ("id"),
    CONSTRAINT "fk_match_results_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_match_results_job" FOREIGN KEY ("job_id") REFERENCES "jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "uq_match_results_user_job" UNIQUE ("user_id", "job_id")
);

-- CreateIndices for match_results
CREATE INDEX IF NOT EXISTS "idx_match_results_user_id" ON "match_results"("user_id");
CREATE INDEX IF NOT EXISTS "idx_match_results_job_id" ON "match_results"("job_id");
CREATE INDEX IF NOT EXISTS "idx_match_results_overall_score" ON "match_results"("overall_score" DESC);
CREATE INDEX IF NOT EXISTS "idx_match_results_user_score" ON "match_results"("user_id", "overall_score" DESC);
