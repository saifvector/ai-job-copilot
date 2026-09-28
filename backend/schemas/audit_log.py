import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditLogCreate(BaseModel):
    """Schema for creating a new audit log entry."""
    user_id: Optional[uuid.UUID] = Field(None, description="Optional user initiating the audited action")
    action: str = Field(..., max_length=100, description="Audited event name (e.g. RESUME_UPLOAD, PROFILE_UPDATE)")
    resource: str = Field(..., max_length=100, description="Resource type acted upon")
    resource_id: Optional[str] = Field(None, max_length=255, description="Resource unique identifier")
    details: Optional[Dict[str, Any]] = Field(None, description="Structured metadata dictionary")
    ip_address: Optional[str] = Field(None, max_length=45, description="Client IPv4/IPv6 address")
    user_agent: Optional[str] = Field(None, max_length=512, description="Client user agent string")


class AuditLogResponse(BaseModel):
    """Schema returned for an individual audit log."""
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Paginated list of audit logs."""
    total: int
    items: List[AuditLogResponse]
    limit: int
    offset: int
