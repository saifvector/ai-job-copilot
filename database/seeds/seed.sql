-- SQL Seed script for PostgreSQL Docker container init or manual seeding
-- Inserts initial demo user and profile with idempotent DO NOTHING on conflict

INSERT INTO "users" ("id", "name", "email", "created_at", "updated_at")
VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'Alex Chen',
    'alex.chen@example.com',
    NOW(),
    NOW()
)
ON CONFLICT ("email") DO UPDATE SET "name" = EXCLUDED."name";

INSERT INTO "profiles" (
    "id",
    "user_id",
    "preferred_roles",
    "preferred_locations",
    "years_of_experience",
    "resume_url",
    "created_at",
    "updated_at"
)
VALUES (
    'b0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    ARRAY['Staff Software Engineer', 'Full Stack Architect', 'AI Solutions Engineer'],
    ARRAY['Remote', 'San Francisco, CA', 'New York, NY'],
    8,
    'https://storage.jobcopilot.dev/resumes/alex-chen-sample.pdf',
    NOW(),
    NOW()
)
ON CONFLICT ("user_id") DO UPDATE SET
    "preferred_roles" = EXCLUDED."preferred_roles",
    "preferred_locations" = EXCLUDED."preferred_locations",
    "years_of_experience" = EXCLUDED."years_of_experience";
