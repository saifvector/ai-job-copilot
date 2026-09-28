-- Migration: 20260928000014_add_agent_orchestration_layer
-- Description: Phase 15 - AI Agent Orchestration Layer, Multi-Agent Collaboration, Task System, Agent Memory, and Workflow Executions

-- CreateTable: workflow_executions
CREATE TABLE IF NOT EXISTS "workflow_executions" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "workflow_type" VARCHAR(100) NOT NULL,
    "status" VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    "current_step" VARCHAR(100),
    "steps" TEXT NOT NULL,
    "context" TEXT NOT NULL,
    "duration_ms" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "workflow_executions_pkey" PRIMARY KEY ("id")
);

-- CreateTable: agent_tasks
CREATE TABLE IF NOT EXISTS "agent_tasks" (
    "id" UUID NOT NULL,
    "user_id" UUID,
    "agent" VARCHAR(100) NOT NULL,
    "workflow_execution_id" UUID,
    "status" VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    "payload" TEXT NOT NULL,
    "result" TEXT,
    "error_message" TEXT,
    "model_used" VARCHAR(100),
    "duration_ms" DOUBLE PRECISION,
    "retry_count" INTEGER NOT NULL DEFAULT 0,
    "max_retries" INTEGER NOT NULL DEFAULT 3,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completed_at" TIMESTAMPTZ,

    CONSTRAINT "agent_tasks_pkey" PRIMARY KEY ("id")
);

-- CreateTable: agent_memories
CREATE TABLE IF NOT EXISTS "agent_memories" (
    "id" UUID NOT NULL,
    "user_id" UUID NOT NULL,
    "agent" VARCHAR(100) NOT NULL,
    "memory_type" VARCHAR(50) NOT NULL,
    "content" TEXT NOT NULL,
    "relevance_score" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "agent_memories_pkey" PRIMARY KEY ("id")
);

-- CreateIndexes
CREATE INDEX IF NOT EXISTS "idx_workflow_executions_user_id" ON "workflow_executions"("user_id");
CREATE INDEX IF NOT EXISTS "idx_workflow_executions_type" ON "workflow_executions"("workflow_type");
CREATE INDEX IF NOT EXISTS "idx_workflow_executions_status" ON "workflow_executions"("status");
CREATE INDEX IF NOT EXISTS "idx_workflow_executions_created_at" ON "workflow_executions"("created_at");

CREATE INDEX IF NOT EXISTS "idx_agent_tasks_user_id" ON "agent_tasks"("user_id");
CREATE INDEX IF NOT EXISTS "idx_agent_tasks_agent" ON "agent_tasks"("agent");
CREATE INDEX IF NOT EXISTS "idx_agent_tasks_status" ON "agent_tasks"("status");
CREATE INDEX IF NOT EXISTS "idx_agent_tasks_workflow_id" ON "agent_tasks"("workflow_execution_id");
CREATE INDEX IF NOT EXISTS "idx_agent_tasks_created_at" ON "agent_tasks"("created_at");

CREATE INDEX IF NOT EXISTS "idx_agent_memories_user_id" ON "agent_memories"("user_id");
CREATE INDEX IF NOT EXISTS "idx_agent_memories_agent" ON "agent_memories"("agent");
CREATE INDEX IF NOT EXISTS "idx_agent_memories_type" ON "agent_memories"("memory_type");
CREATE INDEX IF NOT EXISTS "idx_agent_memories_created_at" ON "agent_memories"("created_at");

-- AddForeignKeys
ALTER TABLE "workflow_executions"
    ADD CONSTRAINT "fk_workflow_executions_user_id"
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "agent_tasks"
    ADD CONSTRAINT "fk_agent_tasks_user_id"
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE "agent_tasks"
    ADD CONSTRAINT "fk_agent_tasks_workflow_id"
    FOREIGN KEY ("workflow_execution_id") REFERENCES "workflow_executions"("id") ON DELETE SET NULL ON UPDATE CASCADE;

ALTER TABLE "agent_memories"
    ADD CONSTRAINT "fk_agent_memories_user_id"
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
