-- Migration: 20260927000003_add_job_discovery
-- Description: Creates jobs and job_skills tables for Phase 4 Job Discovery Engine

-- CreateTable
CREATE TABLE IF NOT EXISTS "jobs" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "source" VARCHAR(100) NOT NULL,
    "external_id" VARCHAR(255) NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "company" VARCHAR(255) NOT NULL,
    "location" VARCHAR(255) NOT NULL,
    "employment_type" VARCHAR(100),
    "salary_min" DECIMAL(12, 2),
    "salary_max" DECIMAL(12, 2),
    "currency" VARCHAR(10),
    "description" TEXT NOT NULL,
    "requirements" TEXT,
    "apply_url" TEXT NOT NULL,
    "company_website" VARCHAR(255),
    "posted_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_jobs" PRIMARY KEY ("id"),
    CONSTRAINT "uq_jobs_source_external_id" UNIQUE ("source", "external_id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "job_skills" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "job_id" UUID NOT NULL,
    "skill_name" VARCHAR(100) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_job_skills" PRIMARY KEY ("id"),
    CONSTRAINT "fk_job_skills_job" FOREIGN KEY ("job_id") REFERENCES "jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndices for jobs
CREATE INDEX IF NOT EXISTS "idx_jobs_company_title" ON "jobs"("company", "title");
CREATE INDEX IF NOT EXISTS "idx_jobs_location" ON "jobs"("location");
CREATE INDEX IF NOT EXISTS "idx_jobs_source" ON "jobs"("source");
CREATE INDEX IF NOT EXISTS "idx_jobs_posted_at" ON "jobs"("posted_at");

-- CreateIndices for job_skills
CREATE INDEX IF NOT EXISTS "idx_job_skills_job_id" ON "job_skills"("job_id");
CREATE INDEX IF NOT EXISTS "idx_job_skills_skill_name" ON "job_skills"("skill_name");
