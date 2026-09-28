-- Migration: 20260927000005_add_analytics_snapshots
-- Description: Creates analytics_snapshots table for Phase 6 Dashboard and Analytics Workspace

-- CreateTable
CREATE TABLE IF NOT EXISTS "analytics_snapshots" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "profile_score" DECIMAL(5, 2) NOT NULL,
    "readiness_score" DECIMAL(5, 2) NOT NULL,
    "average_match_score" DECIMAL(5, 2) NOT NULL,
    "excellent_matches" INTEGER NOT NULL DEFAULT 0,
    "strong_matches" INTEGER NOT NULL DEFAULT 0,
    "moderate_matches" INTEGER NOT NULL DEFAULT 0,
    "weak_matches" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "pk_analytics_snapshots" PRIMARY KEY ("id"),
    CONSTRAINT "fk_analytics_snapshots_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndex
CREATE INDEX IF NOT EXISTS "idx_analytics_snapshots_user_created" ON "analytics_snapshots"("user_id", "created_at" DESC);
