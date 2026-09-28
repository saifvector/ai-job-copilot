-- AI Job Copilot Database Migration: 20260927000002_add_resume_intelligence
-- Target: PostgreSQL 15+

-- AlterTable: users
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "phone" VARCHAR(50);

-- AlterTable: profiles
ALTER TABLE "profiles" ADD COLUMN IF NOT EXISTS "summary" TEXT;

-- CreateTable: skills
CREATE TABLE "skills" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "category" VARCHAR(50) NOT NULL,
    "confidence_score" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "skills_pkey" PRIMARY KEY ("id")
);

-- CreateTable: projects
CREATE TABLE "projects" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "technologies" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "projects_pkey" PRIMARY KEY ("id")
);

-- CreateTable: education
CREATE TABLE "education" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "institution" VARCHAR(255) NOT NULL,
    "degree" VARCHAR(255) NOT NULL,
    "field_of_study" VARCHAR(255),
    "start_date" VARCHAR(50),
    "end_date" VARCHAR(50),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "education_pkey" PRIMARY KEY ("id")
);

-- CreateTable: experience
CREATE TABLE "experience" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "company" VARCHAR(255) NOT NULL,
    "role" VARCHAR(255) NOT NULL,
    "description" TEXT NOT NULL,
    "start_date" VARCHAR(50),
    "end_date" VARCHAR(50),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "experience_pkey" PRIMARY KEY ("id")
);

-- CreateTable: certifications
CREATE TABLE "certifications" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "issuer" VARCHAR(255) NOT NULL,
    "issue_date" VARCHAR(50),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "certifications_pkey" PRIMARY KEY ("id")
);

-- Indexes
CREATE INDEX "idx_skills_user_id" ON "skills"("user_id");
CREATE INDEX "idx_skills_category" ON "skills"("category");
CREATE INDEX "idx_projects_user_id" ON "projects"("user_id");
CREATE INDEX "idx_education_user_id" ON "education"("user_id");
CREATE INDEX "idx_experience_user_id" ON "experience"("user_id");
CREATE INDEX "idx_certifications_user_id" ON "certifications"("user_id");

-- Foreign Keys with Cascade Delete
ALTER TABLE "skills" ADD CONSTRAINT "skills_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "projects" ADD CONSTRAINT "projects_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "education" ADD CONSTRAINT "education_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "experience" ADD CONSTRAINT "experience_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "certifications" ADD CONSTRAINT "certifications_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
