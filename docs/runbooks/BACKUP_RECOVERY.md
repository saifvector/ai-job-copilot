# AI Job Copilot - Backup & Disaster Recovery Guide

## 1. Backup Strategy & Objectives

| Objective | Target | Implementation |
|---|---|---|
| **Recovery Point Objective (RPO)** | < 1 hour (Continuous WAL) / < 24 hours (Snapshots) | Daily automated full snapshot + continuous write-ahead logging. |
| **Recovery Time Objective (RTO)** | < 15 minutes | Single-command dry-run and live restore via `BackupService`. |
| **Data Integrity Guarantee** | 100% Verified | SHA-256 cryptographic checksums and JSON manifest verification. |
| **Retention Policy** | 30 Days | Rolling window; backups older than 30 days are pruned automatically. |

---

## 2. Backup Architecture & Manifest Format

Each backup created by `BackupService` produces two files in the designated backup directory (`./backups` or Cloud Storage bucket):
1. **The Backup Archive**: `<backup_name>` (e.g., `backup_20260928_120000.db` or `.sql.gz`).
2. **The Verification Manifest**: `<backup_name>.manifest.json`.

### Manifest Specification Example:
```json
{
  "backup_id": "backup_20260928_120000",
  "filename": "backup_20260928_120000.db",
  "size_bytes": 1048576,
  "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "created_at": "2026-09-28T12:00:00Z",
  "environment": "production",
  "db_type": "sqlite",
  "version": "1.0.0"
}
```

---

## 3. Creating Backups

### 3.1 Via API Endpoint (Recommended)
```bash
curl -X POST http://localhost:8000/api/v1/system/backups/create \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"notes": "Pre-deployment migration backup"}'
```

### 3.2 Programmatically via Python CLI
```bash
python -c "
import asyncio
from backend.services.backup_service import BackupService
from backend.core.config import settings

async def run():
    service = BackupService(backup_dir=settings.BACKUP_DIR, db_url=settings.DATABASE_URL)
    meta = await service.create_backup(notes='CLI scheduled backup')
    print('Created backup:', meta.backup_id, 'Checksum:', meta.checksum_sha256)

asyncio.run(run())
"
```

---

## 4. Validating Backup Integrity

Before executing any restore operation, validate that the backup archive has not suffered bit rot or corruption.

### 4.1 Via API Validation Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/system/backups/validate \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"backup_id": "backup_20260928_120000"}'
```

The system recalculates the SHA-256 hash of the archive on disk, cross-references it with the recorded manifest, tests the database structure, and returns:
```json
{
  "backup_id": "backup_20260928_120000",
  "is_valid": true,
  "checksum_matches": true,
  "size_matches": true,
  "readable": true,
  "error_message": null
}
```

---

## 5. Restoration Procedures

### 5.1 Dry-Run Simulation (Always Run First)
A dry run verifies checksums, tests archive uncompression, and validates permissions without altering the active production database.

```bash
curl -X POST http://localhost:8000/api/v1/system/backups/restore \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"backup_id": "backup_20260928_120000", "dry_run": true}'
```

### 5.2 Live Automated Restoration
```bash
curl -X POST http://localhost:8000/api/v1/system/backups/restore \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{"backup_id": "backup_20260928_120000", "dry_run": false}'
```

### 5.3 Manual PostgreSQL Emergency Restore (Disaster Recovery)

If the API service is unavailable, restore directly from the database host:

1. **Stop Incoming Traffic**:
   ```bash
   kubectl scale deployment/backend-api --replicas=0 -n ai-job-copilot
   ```
2. **Verify Checksum**:
   ```bash
   sha256sum backup_20260928_120000.sql.gz
   # Compare against manifest JSON
   ```
3. **Drop and Recreate Clean Database**:
   ```bash
   dropdb -U job_copilot -h localhost job_copilot_prod
   createdb -U job_copilot -h localhost job_copilot_prod
   ```
4. **Restore Database Contents**:
   ```bash
   gunzip -c backup_20260928_120000.sql.gz | psql -U job_copilot -h localhost -d job_copilot_prod
   ```
5. **Run Prisma Migration Safety Verification**:
   ```bash
   npx prisma migrate status
   ```
6. **Resume Traffic**:
   ```bash
   kubectl scale deployment/backend-api --replicas=3 -n ai-job-copilot
   ```

---

## 6. Retention & Pruning Policy

By default, backups older than 30 days are automatically pruned during the daily maintenance cycle:
```bash
python -c "
import asyncio
from backend.services.backup_service import BackupService
from backend.core.config import settings

async def run():
    service = BackupService(backup_dir=settings.BACKUP_DIR, db_url=settings.DATABASE_URL)
    deleted = await service.prune_old_backups(retention_days=30)
    print(f'Pruned {len(deleted)} expired backups.')

asyncio.run(run())
"
```

---

## 7. Disaster Recovery Drill Schedule

To guarantee business continuity:
1. **Bi-weekly**: Automated dry-run validation of the latest backup in staging.
2. **Quarterly**: Full live restoration drill into an isolated recovery environment with end-to-end user regression testing.
