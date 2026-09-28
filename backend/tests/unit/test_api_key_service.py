import uuid
from datetime import datetime, timedelta, timezone
import pytest
from core.exceptions import AuthenticationError, AuthorizationError
from core.security.api_keys import ApiKeyService, API_KEY_PREFIX


@pytest.mark.asyncio
async def test_generate_and_hash_api_key(db_session):
    raw_key, key_hash, prefix = ApiKeyService.generate_key()

    assert raw_key.startswith(API_KEY_PREFIX)
    assert len(raw_key) > 30
    assert len(key_hash) == 64  # SHA-256 hex digest length
    assert prefix.startswith(API_KEY_PREFIX[:8])
    assert prefix.endswith(raw_key[-4:])
    assert ApiKeyService.hash_key(raw_key) == key_hash


@pytest.mark.asyncio
async def test_create_and_validate_api_key(db_session):
    service = ApiKeyService(db_session)
    user_id = uuid.uuid4()

    key_model, raw_key = await service.create_api_key(
        user_id=user_id,
        name="Production Partner API",
        scopes=["read:profile", "read:matches", "write:applications"],
        rate_limit=120,
        monthly_limit=50000,
        expires_in_days=30,
    )

    assert key_model.id is not None
    assert key_model.name == "Production Partner API"
    assert key_model.rate_limit == 120
    assert key_model.is_active is True
    assert key_model.expires_at is not None

    # Validate key successfully
    validated = await service.validate_api_key(
        raw_key=raw_key,
        required_scopes=["read:profile"],
    )
    assert validated.id == key_model.id
    assert validated.user_id == user_id


@pytest.mark.asyncio
async def test_validate_api_key_missing_scope(db_session):
    service = ApiKeyService(db_session)
    user_id = uuid.uuid4()

    _, raw_key = await service.create_api_key(
        user_id=user_id,
        name="Read Only Key",
        scopes=["read:profile"],
    )

    with pytest.raises(AuthorizationError) as exc_info:
        await service.validate_api_key(raw_key=raw_key, required_scopes=["write:applications"])

    assert "missing required scope" in str(exc_info.value)


@pytest.mark.asyncio
async def test_rotate_api_key(db_session):
    service = ApiKeyService(db_session)
    user_id = uuid.uuid4()

    old_key, old_raw = await service.create_api_key(
        user_id=user_id,
        name="Key To Rotate",
        scopes=["read:profile", "read:reports"],
    )

    new_key, new_raw = await service.rotate_api_key(
        key_id=old_key.id,
        user_id=user_id,
        expires_in_days=60,
    )

    assert new_key.id != old_key.id
    assert "Rotated" in new_key.name
    assert new_key.scopes == old_key.scopes
    assert new_key.is_active is True

    # Old key is deactivated
    with pytest.raises(AuthenticationError):
        await service.validate_api_key(raw_key=old_raw)

    # New key is active and valid
    validated_new = await service.validate_api_key(raw_key=new_raw)
    assert validated_new.id == new_key.id


@pytest.mark.asyncio
async def test_revoke_api_key(db_session):
    service = ApiKeyService(db_session)
    user_id = uuid.uuid4()

    key, raw_key = await service.create_api_key(
        user_id=user_id,
        name="Disposable Key",
    )

    success = await service.repo.revoke_key(key_id=key.id, user_id=user_id)
    assert success is True

    with pytest.raises(AuthenticationError):
        await service.validate_api_key(raw_key=raw_key)
