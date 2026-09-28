-- Phase 9: Reporting & Export Center Migration
-- Create reports table with user foreign key and performance indexes

CREATE TABLE IF NOT EXISTS "reports" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "report_type" VARCHAR(50) NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "format" VARCHAR(10) NOT NULL,
    "file_path" VARCHAR(500) NOT NULL,
    "file_name" VARCHAR(255) NOT NULL,
    "file_size" INTEGER NOT NULL DEFAULT 0,
    "download_count" INTEGER NOT NULL DEFAULT 0,
    "generation_duration_ms" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "summary" TEXT,
    "generated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "reports_pkey" PRIMARY KEY ("id")
);

-- CreateIndexes
CREATE INDEX IF NOT EXISTS "idx_reports_user_id" ON "reports"("user_id");
CREATE INDEX IF NOT EXISTS "idx_reports_report_type" ON "reports"("report_type");
CREATE INDEX IF NOT EXISTS "idx_reports_generated_at" ON "reports"("generated_at");

-- AddForeignKey
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'reports_user_id_fkey'
    ) THEN
        ALTER TABLE "reports" ADD CONSTRAINT "reports_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END $$;
