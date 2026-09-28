-- Phase 14: Extensible Platform, Public API, Webhooks, Integrations, and Developer Portal
-- Creates api_keys, webhooks, webhook_delivery_logs, oauth_connections, and api_usage_logs

CREATE TABLE IF NOT EXISTS "api_keys" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "key_hash" VARCHAR(255) NOT NULL,
    "prefix" VARCHAR(32) NOT NULL,
    "scopes" TEXT[] NOT NULL DEFAULT ARRAY['read:profile', 'read:resume', 'read:matches', 'read:applications', 'read:reports']::TEXT[],
    "rate_limit" INTEGER NOT NULL DEFAULT 60,
    "monthly_limit" INTEGER NOT NULL DEFAULT 10000,
    "expires_at" TIMESTAMP(3),
    "last_used_at" TIMESTAMP(3),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "api_keys_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "fk_api_keys_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "uq_api_keys_key_hash" UNIQUE ("key_hash")
);

CREATE INDEX IF NOT EXISTS "idx_api_keys_user_id" ON "api_keys"("user_id");
CREATE INDEX IF NOT EXISTS "idx_api_keys_key_hash" ON "api_keys"("key_hash");
CREATE INDEX IF NOT EXISTS "idx_api_keys_prefix" ON "api_keys"("prefix");
CREATE INDEX IF NOT EXISTS "idx_api_keys_is_active" ON "api_keys"("is_active");

CREATE TABLE IF NOT EXISTS "webhooks" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "endpoint" VARCHAR(1024) NOT NULL,
    "secret" VARCHAR(255) NOT NULL,
    "events" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "enabled" BOOLEAN NOT NULL DEFAULT true,
    "failure_count" INTEGER NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "webhooks_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "fk_webhooks_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_webhooks_user_id" ON "webhooks"("user_id");
CREATE INDEX IF NOT EXISTS "idx_webhooks_enabled" ON "webhooks"("enabled");

CREATE TABLE IF NOT EXISTS "webhook_delivery_logs" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "webhook_id" UUID NOT NULL,
    "event" VARCHAR(100) NOT NULL,
    "payload" TEXT NOT NULL,
    "response_status" INTEGER,
    "response_body" TEXT,
    "duration_ms" DOUBLE PRECISION,
    "attempt" INTEGER NOT NULL DEFAULT 1,
    "success" BOOLEAN NOT NULL DEFAULT false,
    "error" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "webhook_delivery_logs_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "fk_webhook_delivery_logs_webhook" FOREIGN KEY ("webhook_id") REFERENCES "webhooks"("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS "idx_webhook_delivery_logs_webhook_id" ON "webhook_delivery_logs"("webhook_id");
CREATE INDEX IF NOT EXISTS "idx_webhook_delivery_logs_event" ON "webhook_delivery_logs"("event");
CREATE INDEX IF NOT EXISTS "idx_webhook_delivery_logs_success" ON "webhook_delivery_logs"("success");
CREATE INDEX IF NOT EXISTS "idx_webhook_delivery_logs_created_at" ON "webhook_delivery_logs"("created_at");

CREATE TABLE IF NOT EXISTS "oauth_connections" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID NOT NULL,
    "provider" VARCHAR(50) NOT NULL,
    "provider_user_id" VARCHAR(255),
    "access_token" TEXT,
    "refresh_token" TEXT,
    "expires_at" TIMESTAMP(3),
    "scopes" TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    "metadata" TEXT,
    "status" VARCHAR(50) NOT NULL DEFAULT 'connected',
    "last_sync_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "oauth_connections_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "fk_oauth_connections_user" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "uq_oauth_connections_user_provider" UNIQUE ("user_id", "provider")
);

CREATE INDEX IF NOT EXISTS "idx_oauth_connections_user_id" ON "oauth_connections"("user_id");
CREATE INDEX IF NOT EXISTS "idx_oauth_connections_provider" ON "oauth_connections"("provider");
CREATE INDEX IF NOT EXISTS "idx_oauth_connections_status" ON "oauth_connections"("status");

CREATE TABLE IF NOT EXISTS "api_usage_logs" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" UUID,
    "api_key_id" UUID,
    "endpoint" VARCHAR(255) NOT NULL,
    "method" VARCHAR(10) NOT NULL,
    "status_code" INTEGER NOT NULL,
    "latency_ms" DOUBLE PRECISION NOT NULL,
    "ip_address" VARCHAR(45),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "api_usage_logs_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "idx_api_usage_logs_user_id" ON "api_usage_logs"("user_id");
CREATE INDEX IF NOT EXISTS "idx_api_usage_logs_api_key_id" ON "api_usage_logs"("api_key_id");
CREATE INDEX IF NOT EXISTS "idx_api_usage_logs_endpoint" ON "api_usage_logs"("endpoint");
CREATE INDEX IF NOT EXISTS "idx_api_usage_logs_created_at" ON "api_usage_logs"("created_at");
