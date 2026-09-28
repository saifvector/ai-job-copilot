-- Migration: 20260927000009_add_recruiter_crm
-- Phase 10: Recruiter CRM and Networking Intelligence System

-- 1. Create recruiters table
CREATE TABLE IF NOT EXISTS "recruiters" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "company" VARCHAR(255) NOT NULL,
    "title" VARCHAR(255),
    "email" VARCHAR(255),
    "linkedin_url" VARCHAR(500),
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_recruiters" PRIMARY KEY ("id"),
    CONSTRAINT "fk_recruiters_user_id" FOREIGN KEY ("user_id") 
        REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_recruiters_user_id" ON "recruiters"("user_id");
CREATE INDEX IF NOT EXISTS "idx_recruiters_company" ON "recruiters"("company");
CREATE INDEX IF NOT EXISTS "idx_recruiters_created_at" ON "recruiters"("created_at");

-- 2. Create referrals table
CREATE TABLE IF NOT EXISTS "referrals" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "recruiter_id" UUID NOT NULL,
    "company" VARCHAR(255) NOT NULL,
    "role" VARCHAR(255) NOT NULL,
    "status" VARCHAR(50) NOT NULL DEFAULT 'Requested',
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_referrals" PRIMARY KEY ("id"),
    CONSTRAINT "fk_referrals_recruiter_id" FOREIGN KEY ("recruiter_id") 
        REFERENCES "recruiters"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_referrals_recruiter_id" ON "referrals"("recruiter_id");
CREATE INDEX IF NOT EXISTS "idx_referrals_status" ON "referrals"("status");
CREATE INDEX IF NOT EXISTS "idx_referrals_company" ON "referrals"("company");

-- 3. Create contact_interactions table
CREATE TABLE IF NOT EXISTS "contact_interactions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "recruiter_id" UUID NOT NULL,
    "interaction_type" VARCHAR(50) NOT NULL,
    "summary" TEXT NOT NULL,
    "interaction_date" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_contact_interactions" PRIMARY KEY ("id"),
    CONSTRAINT "fk_contact_interactions_recruiter_id" FOREIGN KEY ("recruiter_id") 
        REFERENCES "recruiters"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_contact_interactions_recruiter_id" ON "contact_interactions"("recruiter_id");
CREATE INDEX IF NOT EXISTS "idx_contact_interactions_date" ON "contact_interactions"("interaction_date");
CREATE INDEX IF NOT EXISTS "idx_contact_interactions_type" ON "contact_interactions"("interaction_type");
