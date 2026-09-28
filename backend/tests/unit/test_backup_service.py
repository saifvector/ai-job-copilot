import os
import pytest
from services.backup_service import BackupService


@pytest.mark.asyncio
async def test_backup_service_create_and_validate(tmp_path):
    backup_dir = str(tmp_path / "backups")
    service = BackupService(backup_dir=backup_dir)

    # 1. Create Backup
    manifest = await service.create_backup(backup_type="unit_test", notes="Test snapshot")
    assert manifest["backup_id"].startswith("backup_unit_test_")
    assert manifest["size_bytes"] > 0
    assert len(manifest["sha256_checksum"]) == 64
    assert os.path.exists(manifest["file_path"])

    # 2. Validate Backup
    validation = await service.validate_backup(manifest["backup_id"])
    assert validation["is_valid"] is True
    assert validation["checksum_verified"] is True
    assert validation["schema_integrity_ok"] is True


@pytest.mark.asyncio
async def test_backup_service_dry_run_restore(tmp_path):
    backup_dir = str(tmp_path / "backups")
    service = BackupService(backup_dir=backup_dir)

    manifest = await service.create_backup(backup_type="daily")
    restore_result = await service.restore_backup(
        backup_id=manifest["backup_id"],
        dry_run=True,
    )

    assert restore_result["success"] is True
    assert restore_result["dry_run"] is True


@pytest.mark.asyncio
async def test_backup_service_retention_pruning(tmp_path):
    backup_dir = str(tmp_path / "backups")
    service = BackupService(backup_dir=backup_dir)

    # Create backup with retention_days=0 so it gets pruned immediately
    manifest = await service.create_backup(backup_type="daily")
    assert len(await service.list_backups()) == 1

    # Prune with 0 days retention
    pruned = await service.apply_retention_policy(retention_days=-1)
    assert pruned == 1
    assert len(await service.list_backups()) == 0
