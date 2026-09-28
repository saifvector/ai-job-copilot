from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatabaseHealthResponse(BaseModel):
    """Health status and performance of database connectivity and connection pool."""
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    connected: bool
    latency_ms: float
    pool_size: Optional[int] = None
    checked_in: Optional[int] = None
    checked_out: Optional[int] = None
    overflow: Optional[int] = None
    dialect: str = "postgresql"
    migration_status: str = "synced"
    error: Optional[str] = None


class CacheHealthResponse(BaseModel):
    """Health status of Redis or in-memory fallback cache."""
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    connected: bool
    latency_ms: float
    engine: str = Field(..., description="redis or in_memory_fallback")
    active_keys: Optional[int] = 0
    used_memory_human: Optional[str] = "N/A"
    error: Optional[str] = None


class AIHealthResponse(BaseModel):
    """Health status of Gemini AI orchestration engine."""
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    provider: str = "Google Gemini"
    primary_model: str = "gemini-2.5-pro"
    fallback_model: str = "gemini-2.5-flash"
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Aggregated production health probe response."""
    status: str = Field(..., description="healthy, degraded, or unhealthy")
    version: str
    environment: str
    uptime_seconds: float
    timestamp: datetime
    database: DatabaseHealthResponse
    cache: CacheHealthResponse
    ai: AIHealthResponse


class LatencyPercentiles(BaseModel):
    """Latency distribution percentiles."""
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    total_requests: int


class MonitoringMetricsResponse(BaseModel):
    """Detailed production monitoring metrics."""
    timestamp: datetime
    uptime_seconds: float
    api_latency: LatencyPercentiles
    error_rates_by_category: Dict[str, int]
    total_errors: int
    ai_metrics: Dict[str, Any]
    database_metrics: Dict[str, Any]
    cache_metrics: Dict[str, Any]
    system_resources: Dict[str, Any]
