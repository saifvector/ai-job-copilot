-- Migration: 20260927000006_add_tailored_resumes
-- Description: Creates tailored_resumes table for Phase 7 AI Resume Tailoring Engine

-- CreateTable
CREATE TABLE IF NOT EXISTS "tailored_resumes" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "job_id" UUID NOT NULL,
    "original_resume_id" UUID,
    "title" VARCHAR(255) NOT NULL,
    "summary" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "ats_score" DECIMAL(5, 2) NOT NULL DEFAULT 0.0,
    "keyword_coverage" DECIMAL(5, 2) NOT NULL DEFAULT 0.0,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_tailored_resumes" PRIMARY KEY ("id"),
    CONSTRAINT "fk_tailored_resumes_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_tailored_resumes_job" FOREIGN KEY ("job_id") REFERENCES "jobs"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_tailored_resumes_original_resume" FOREIGN KEY ("original_resume_id") REFERENCES "resumes"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_tailored_resumes_user_id" ON "tailored_resumes"("user_id");
CREATE INDEX IF NOT EXISTS "idx_tailored_resumes_job_id" ON "tailored_resumes"("job_id");
CREATE INDEX IF NOT EXISTS "idx_tailored_resumes_user_job" ON "tailored_resumes"("user_id", "job_id");
