from datetime import datetime, timezone
import uuid
from typing import Any, Dict


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def is_valid_uuid(val: Any) -> bool:
    """Check if value is a valid UUID string or UUID instance."""
    if isinstance(val, uuid.UUID):
        return True
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}
