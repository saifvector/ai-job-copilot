-- AI Job Copilot Database Migration: 20260927000001_add_resume
-- Target: PostgreSQL 15+

-- CreateTable: resumes
CREATE TABLE "resumes" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "original_filename" VARCHAR(255) NOT NULL,
    "stored_filename" VARCHAR(255) NOT NULL,
    "file_type" VARCHAR(100) NOT NULL,
    "file_size" INTEGER NOT NULL,
    "file_path" TEXT NOT NULL,
    "uploaded_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "resumes_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "resumes_user_id_key" ON "resumes"("user_id");
CREATE INDEX "idx_resumes_user_id" ON "resumes"("user_id");

-- AddForeignKey
ALTER TABLE "resumes" ADD CONSTRAINT "resumes_user_id_fkey" 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") 
    ON DELETE CASCADE ON UPDATE CASCADE;
