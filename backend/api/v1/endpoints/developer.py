import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_authenticated_user_id, get_db
from core.security.api_keys import ApiKeyService
from integrations.manager import IntegrationManager
from plugins.sdk import BasePlugin, PluginManifest, PluginRegistry
from schemas.platform import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
    ApiKeyRotateRequest,
    ApiAnalyticsSummaryResponse,
    IntegrationListResponse,
    OAuthConnectRequest,
    OAuthConnectionResponse,
    OAuthSyncResponse,
    PluginExecuteHookRequest,
    PluginExecuteHookResponse,
    PluginListResponse,
    PluginManifestResponse,
    PluginRegisterRequest,
)
from services.api_analytics_service import ApiAnalyticsService

router = APIRouter(prefix="/developer", tags=["Developer Portal"])


# --- API Key Management ---

@router.get("/keys", response_model=ApiKeyListResponse)
async def list_api_keys(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List developer API keys for the current user."""
    service = ApiKeyService(db)
    items, total = await service.repo.list_by_user(user_id=user_id, limit=limit, offset=offset)
    return {"items": items, "total": total}


@router.post("/keys", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    body: ApiKeyCreate,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate a new API key. The raw_key will be displayed ONCE in the response."""
    service = ApiKeyService(db)
    key_model, raw_key = await service.create_api_key(
        user_id=user_id,
        name=body.name,
        scopes=body.scopes,
        rate_limit=body.rate_limit or 60,
        monthly_limit=body.monthly_limit or 10000,
        expires_in_days=body.expires_in_days,
    )
    return {
        "id": key_model.id,
        "user_id": key_model.user_id,
        "name": key_model.name,
        "prefix": key_model.prefix,
        "scopes": key_model.scopes,
        "rate_limit": key_model.rate_limit,
        "monthly_limit": key_model.monthly_limit,
        "expires_at": key_model.expires_at,
        "last_used_at": key_model.last_used_at,
        "is_active": key_model.is_active,
        "created_at": key_model.created_at,
        "updated_at": key_model.updated_at,
        "raw_key": raw_key,
    }


@router.post("/keys/{key_id}/rotate", response_model=ApiKeyCreatedResponse)
async def rotate_api_key(
    key_id: uuid.UUID,
    body: Optional[ApiKeyRotateRequest] = None,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Revoke old key and issue a new replacement key with identical scopes."""
    service = ApiKeyService(db)
    expires_in_days = body.expires_in_days if body else None
    try:
        new_key_model, raw_key = await service.rotate_api_key(
            key_id=key_id,
            user_id=user_id,
            expires_in_days=expires_in_days,
        )
        return {
            "id": new_key_model.id,
            "user_id": new_key_model.user_id,
            "name": new_key_model.name,
            "prefix": new_key_model.prefix,
            "scopes": new_key_model.scopes,
            "rate_limit": new_key_model.rate_limit,
            "monthly_limit": new_key_model.monthly_limit,
            "expires_at": new_key_model.expires_at,
            "last_used_at": new_key_model.last_used_at,
            "is_active": new_key_model.is_active,
            "created_at": new_key_model.created_at,
            "updated_at": new_key_model.updated_at,
            "raw_key": raw_key,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Revoke and deactivate an API key."""
    service = ApiKeyService(db)
    success = await service.repo.revoke_key(key_id=key_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return None


# --- API Usage Analytics ---

@router.get("/analytics", response_model=ApiAnalyticsSummaryResponse)
async def get_api_analytics(
    days: int = Query(default=30, ge=1, le=90),
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve usage analytics: request volume, error rates, p95 latency, and endpoint breakdown."""
    service = ApiAnalyticsService(db)
    summary = await service.get_analytics_summary(user_id=user_id, days=days)
    return summary


# --- Integrations Management ---

@router.get("/integrations", response_model=IntegrationListResponse)
async def list_integrations(
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all third-party integrations (Gmail, Outlook, GCal, Drive, Dropbox, Slack) and connection state."""
    manager = IntegrationManager(db)
    items = await manager.list_integrations_for_user(user_id)
    return {"items": items, "total": len(items)}


@router.post("/integrations/{provider}/connect", response_model=OAuthConnectionResponse)
async def connect_integration(
    provider: str,
    body: Optional[OAuthConnectRequest] = None,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Establish or update an OAuth integration connection."""
    manager = IntegrationManager(db)
    auth_payload = {}
    if body:
        if body.metadata:
            auth_payload.update(body.metadata)
        if body.auth_code:
            auth_payload["auth_code"] = body.auth_code

    try:
        conn = await manager.connect_integration(
            user_id=user_id,
            provider_id=provider,
            auth_payload=auth_payload,
        )
        return conn
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/integrations/{provider}/disconnect", status_code=status.HTTP_200_OK)
async def disconnect_integration(
    provider: str,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect and revoke integration credentials."""
    manager = IntegrationManager(db)
    success = await manager.disconnect_integration(user_id=user_id, provider_id=provider)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found or not connected")
    return {"disconnected": True, "provider": provider}


@router.post("/integrations/{provider}/sync", response_model=OAuthSyncResponse)
async def sync_integration(
    provider: str,
    user_id: uuid.UUID = Depends(get_authenticated_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger an asynchronous synchronization for a connected integration."""
    manager = IntegrationManager(db)
    try:
        result = await manager.sync_integration(user_id=user_id, provider_id=provider)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- Plugin SDK & Ecosystem ---

@router.get("/plugins", response_model=PluginListResponse)
async def list_plugins():
    """List all installed third-party plugins in the platform runtime."""
    registry = PluginRegistry()
    manifests = registry.list_plugins()
    return {"items": manifests, "total": len(manifests)}


@router.post("/plugins/register", response_model=PluginManifestResponse)
async def register_plugin(body: PluginRegisterRequest):
    """Register a custom community plugin into the runtime."""
    registry = PluginRegistry()
    manifest = PluginManifest(
        id=body.id,
        name=body.name,
        version=body.version,
        author=body.author,
        description=body.description,
        capabilities=body.capabilities,
        is_active=True,
    )

    class DynamicPlugin(BasePlugin):
        async def on_custom_analytics(self, context_data):
            res = dict(context_data)
            res[f"plugin_{self.plugin_id}"] = "Custom analytics processed successfully"
            return res

    plugin = DynamicPlugin(manifest, body.config)
    registry.register(plugin)
    return manifest


@router.post("/plugins/{plugin_id}/execute", response_model=PluginExecuteHookResponse)
async def execute_plugin_hook(
    plugin_id: str,
    body: PluginExecuteHookRequest,
):
    """Execute a specific plugin hook."""
    registry = PluginRegistry()
    plugin = registry.get(plugin_id)
    if not plugin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plugin '{plugin_id}' not found")

    try:
        if body.hook_name == "custom_provider":
            res = await plugin.on_custom_job_provider()
        elif body.hook_name == "custom_analytics":
            res = await plugin.on_custom_analytics(body.payload)
        elif body.hook_name == "custom_exporter":
            fmt = body.payload.get("format", "notion")
            res = await plugin.on_custom_export(fmt, body.payload)
        else:
            raise ValueError(f"Unknown hook: {body.hook_name}")

        return {
            "plugin_id": plugin_id,
            "hook_name": body.hook_name,
            "success": True,
            "result": res,
            "error": None,
        }
    except Exception as e:
        return {
            "plugin_id": plugin_id,
            "hook_name": body.hook_name,
            "success": False,
            "result": None,
            "error": str(e),
        }
