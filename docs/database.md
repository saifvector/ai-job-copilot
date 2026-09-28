# Database Architecture & Schema Specification

## Database Engine
* **Target Engine**: PostgreSQL 15+ (PostgreSQL 16 in Docker Compose)
* **Schema Manager**: Prisma ORM
* **Async Runtime Client**: asyncpg / SQLAlchemy 2.0 AsyncEngine

---

## Entity-Relationship Model

```
 ┌─────────────────────────────────────────┐
 │                  User                   │
 ├─────────────────────────────────────────┤
 │ id: UUID [PK, gen_random_uuid()]        │
 │ name: VARCHAR(255)                      │
 │ email: VARCHAR(255) [UNIQUE, INDEX]     │
 │ created_at: TIMESTAMP                   │
 │ updated_at: TIMESTAMP                   │
 └────────────────────┬────────────────────┘
                      │
                      │ 1-to-1 (onDelete: Cascade)
                      │
 ┌────────────────────▼────────────────────┐
 │                 Profile                 │
 ├─────────────────────────────────────────┤
 │ id: UUID [PK, gen_random_uuid()]        │
 │ user_id: UUID [FK -> users.id, UNIQUE]  │
 │ preferred_roles: TEXT[]                 │
 │ preferred_locations: TEXT[]             │
 │ years_of_experience: INTEGER            │
 │ resume_url: TEXT [NULLABLE]             │
 │ created_at: TIMESTAMP                   │
 │ updated_at: TIMESTAMP                   │
 └─────────────────────────────────────────┘
```

---

## Indexing & Constraints Strategy

1. **`users.email`**:
   - `UNIQUE` constraint ensures identity uniqueness.
   - B-Tree index (`idx_users_email`) optimizes lookup latency on authentication and user queries.

2. **`profiles.user_id`**:
   - `UNIQUE` constraint enforces strict 1-to-1 relationship integrity.
   - B-Tree index (`idx_profiles_user_id`) ensures fast joins between `User` and `Profile`.
   - Foreign key constraint specifies `ON DELETE CASCADE ON UPDATE CASCADE`, automatically cleaning up candidate profile data when a user account is deleted.

3. **`preferred_roles` & `preferred_locations`**:
   - Implemented as native PostgreSQL arrays (`TEXT[]`) for high query efficiency without join overhead.
   - Readily extensible to GIN indexing in Phase 2 for substring or array overlap matching.

---

## Database Migrations & Commands

### Generate Client
```bash
npm run generate --workspace=database
```

### Apply Migrations (Local Dev)
```bash
npm run migrate:dev --workspace=database
```

### Deploy Migrations (CI/CD / Production)
```bash
npm run migrate:deploy --workspace=database
```

### Seed Initial Records
```bash
npm run seed --workspace=database
```
