import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


# --- API Key Schemas ---

class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Descriptive label for this API key")
    scopes: Optional[List[str]] = Field(
        default=["read:profile", "read:resume", "read:matches", "read:applications", "read:reports"],
        description="Permission scopes granted to the API key",
    )
    rate_limit: Optional[int] = Field(default=60, ge=1, le=1000, description="Requests permitted per minute")
    monthly_limit: Optional[int] = Field(default=10000, ge=100, le=1000000, description="Requests permitted per calendar month")
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365, description="Optional validity duration in days")


class ApiKeyRotateRequest(BaseModel):
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365, description="New expiration in days")


class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    prefix: str
    scopes: List[str]
    rate_limit: int
    monthly_limit: int
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreatedResponse(ApiKeyResponse):
    raw_key: str = Field(..., description="Full secret API key string. Displayed ONCE to user.")


class ApiKeyListResponse(BaseModel):
    items: List[ApiKeyResponse]
    total: int


# --- Webhook Schemas ---

class WebhookCreate(BaseModel):
    endpoint: str = Field(..., min_length=8, max_length=1024, description="Target HTTP(S) URL for delivery")
    events: List[str] = Field(
        ...,
        description="Event types: resume.parsed, job.matched, report.generated, application.created, application.updated",
    )
    enabled: Optional[bool] = Field(default=True, description="Whether deliveries are active")


class WebhookUpdate(BaseModel):
    endpoint: Optional[str] = Field(None, min_length=8, max_length=1024)
    events: Optional[List[str]] = None
    enabled: Optional[bool] = None


class WebhookDeliveryLogResponse(BaseModel):
    id: uuid.UUID
    webhook_id: uuid.UUID
    event: str
    payload: str
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    duration_ms: Optional[float] = None
    attempt: int
    success: bool
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    endpoint: str
    secret: str
    events: List[str]
    enabled: bool
    failure_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    items: List[WebhookResponse]
    total: int


class WebhookTestRequest(BaseModel):
    event: str = Field(default="job.matched", description="Event name to simulate")
    sample_payload: Optional[Dict[str, Any]] = None


class WebhookTestResponse(BaseModel):
    success: bool
    status_code: Optional[int] = None
    duration_ms: float
    error: Optional[str] = None
    signature: str


# --- Integration Schemas ---

class OAuthConnectRequest(BaseModel):
    auth_code: Optional[str] = Field(None, description="OAuth authorization code from callback")
    scopes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class OAuthConnectionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    provider: str
    provider_user_id: Optional[str] = None
    scopes: List[str]
    status: str
    metadata: Optional[Dict[str, Any]] = None
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def resolve_model_attributes(cls, data: Any) -> Any:
        if hasattr(data, "__tablename__"):
            import json
            meta_val = getattr(data, "metadata_json", None)
            parsed_meta = None
            if meta_val:
                try:
                    parsed_meta = json.loads(meta_val) if isinstance(meta_val, str) else meta_val
                except Exception:
                    parsed_meta = None
            return {
                "id": data.id,
                "user_id": data.user_id,
                "provider": data.provider,
                "provider_user_id": data.provider_user_id,
                "scopes": data.scopes or [],
                "status": data.status,
                "metadata": parsed_meta,
                "last_sync_at": data.last_sync_at,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
        return data


class IntegrationStatusResponse(BaseModel):
    provider: str
    category: str  # email, calendar, storage, notification
    display_name: str
    description: str
    is_connected: bool
    connection: Optional[OAuthConnectionResponse] = None
    capabilities: List[str] = []


class IntegrationListResponse(BaseModel):
    items: List[IntegrationStatusResponse]
    total: int


class OAuthSyncResponse(BaseModel):
    success: bool
    provider: str
    items_synced: int
    details: Dict[str, Any]
    synced_at: datetime


# --- API Analytics Schemas ---

class EndpointUsageBreakdown(BaseModel):
    endpoint: str
    method: str
    request_count: int
    error_count: int
    error_rate: float
    avg_latency_ms: float


class ApiAnalyticsSummaryResponse(BaseModel):
    total_requests: int
    total_errors: int
    error_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    endpoints: List[EndpointUsageBreakdown]
    period: str = "last_30_days"


# --- Plugin SDK Schemas ---

class PluginManifestResponse(BaseModel):
    id: str
    name: str
    version: str
    author: str
    description: str
    capabilities: List[str]  # "custom_provider", "custom_analytics", "custom_exporter"
    is_active: bool = True
    config_schema: Optional[Dict[str, Any]] = None


class PluginRegisterRequest(BaseModel):
    id: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    version: str = Field(default="1.0.0")
    author: str = Field(default="Community Developer")
    description: str = Field(..., min_length=5, max_length=500)
    capabilities: List[str]
    config: Optional[Dict[str, Any]] = None


class PluginExecuteHookRequest(BaseModel):
    hook_name: str
    payload: Dict[str, Any]


class PluginExecuteHookResponse(BaseModel):
    plugin_id: str
    hook_name: str
    success: bool
    result: Any
    error: Optional[str] = None


class PluginListResponse(BaseModel):
    items: List[PluginManifestResponse]
    total: int
