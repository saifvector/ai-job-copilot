-- Migration: 20260927000010_add_interview_preparation
-- Phase 11: AI Interview Preparation Platform

-- 1. Create interview_preparations table
CREATE TABLE IF NOT EXISTS "interview_preparations" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "job_id" UUID,
    "role" VARCHAR(255) NOT NULL,
    "preparation_type" VARCHAR(100) NOT NULL,
    "generated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_interview_preparations" PRIMARY KEY ("id"),
    CONSTRAINT "fk_interview_preparations_user_id" FOREIGN KEY ("user_id") 
        REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "fk_interview_preparations_job_id" FOREIGN KEY ("job_id") 
        REFERENCES "jobs"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_interview_preparations_user_id" ON "interview_preparations"("user_id");
CREATE INDEX IF NOT EXISTS "idx_interview_preparations_job_id" ON "interview_preparations"("job_id");
CREATE INDEX IF NOT EXISTS "idx_interview_preparations_role" ON "interview_preparations"("role");
CREATE INDEX IF NOT EXISTS "idx_interview_preparations_type" ON "interview_preparations"("preparation_type");

-- 2. Create interview_questions table
CREATE TABLE IF NOT EXISTS "interview_questions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "preparation_id" UUID NOT NULL,
    "category" VARCHAR(100) NOT NULL,
    "difficulty" VARCHAR(50) NOT NULL,
    "question" TEXT NOT NULL,
    "sample_answer" TEXT NOT NULL,
    "explanation" TEXT NOT NULL,
    "user_answer" TEXT,
    "score" DOUBLE PRECISION,
    "feedback" TEXT,
    "is_completed" BOOLEAN NOT NULL DEFAULT false,
    "evaluated_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_interview_questions" PRIMARY KEY ("id"),
    CONSTRAINT "fk_interview_questions_preparation_id" FOREIGN KEY ("preparation_id") 
        REFERENCES "interview_preparations"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_questions_preparation_id" ON "interview_questions"("preparation_id");
CREATE INDEX IF NOT EXISTS "idx_questions_category" ON "interview_questions"("category");
CREATE INDEX IF NOT EXISTS "idx_questions_difficulty" ON "interview_questions"("difficulty");
CREATE INDEX IF NOT EXISTS "idx_questions_is_completed" ON "interview_questions"("is_completed");

-- 3. Create mock_interviews table
CREATE TABLE IF NOT EXISTS "mock_interviews" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "role" VARCHAR(255) NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "feedback" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_mock_interviews" PRIMARY KEY ("id"),
    CONSTRAINT "fk_mock_interviews_user_id" FOREIGN KEY ("user_id") 
        REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_mock_interviews_user_id" ON "mock_interviews"("user_id");
CREATE INDEX IF NOT EXISTS "idx_mock_interviews_role" ON "mock_interviews"("role");
CREATE INDEX IF NOT EXISTS "idx_mock_interviews_created_at" ON "mock_interviews"("created_at");
