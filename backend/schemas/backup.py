from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BackupCreateRequest(BaseModel):
    """Request payload to initiate a database snapshot."""
    backup_type: str = Field("manual", description="Backup trigger: manual, daily, pre_migration")
    notes: Optional[str] = Field(None, description="Optional operator note or change reference")


class BackupMetadataResponse(BaseModel):
    """Metadata describing a completed database backup artifact."""
    backup_id: str
    backup_type: str
    filename: str
    file_path: str
    size_bytes: int
    size_human: str
    sha256_checksum: str
    engine: str
    created_at: datetime
    is_valid: bool
    tables_count: int
    notes: Optional[str] = None


class BackupValidationResponse(BaseModel):
    """Validation report verifying backup integrity."""
    backup_id: str
    is_valid: bool
    checksum_verified: bool
    schema_integrity_ok: bool
    tables_detected: List[str]
    size_bytes: int
    checked_at: datetime
    error_message: Optional[str] = None


class BackupRestoreRequest(BaseModel):
    """Request to restore database from backup."""
    backup_id: str
    dry_run: bool = Field(True, description="When true, performs validation and simulation without altering active database")
    confirm: bool = Field(False, description="Explicit operator confirmation flag required for non-dry-run restores")


class BackupRestoreResponse(BaseModel):
    """Result of backup restoration workflow."""
    backup_id: str
    success: bool
    dry_run: bool
    restored_at: datetime
    tables_restored: int
    message: str


class BackupListResponse(BaseModel):
    """List of available backup snapshots."""
    total: int
    retention_days: int
    backups: List[BackupMetadataResponse]
