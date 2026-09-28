from datetime import datetime, timezone
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class HealthStatusResponse(BaseModel):
    """
    Minimal health check response matching user requirement:
    { "status": "healthy" }
    """
    status: str = "healthy"


class DetailedHealthResponse(BaseModel):
    """
    Comprehensive diagnostics response for /api/v1/health
    """
    status: str = "healthy"
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    database: dict[str, Any]


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard envelope for all successful API responses.
    """
    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    data: T
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard envelope for paginated list results.
    """
    items: List[T]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    loc: Optional[List[str | int]] = None
    msg: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Standard error envelope.
    """
    success: bool = False
    error: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
