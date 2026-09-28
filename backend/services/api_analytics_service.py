import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.api_usage_log_repository import ApiUsageLogRepository


class ApiAnalyticsService:
    """
    Service for telemetry ingestion, request duration tracking, and developer portal analytics reporting.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ApiUsageLogRepository(session)

    async def log_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
        user_id: Optional[uuid.UUID] = None,
        api_key_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        await self.repo.log_request(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            user_id=user_id,
            api_key_id=api_key_id,
            ip_address=ip_address,
        )

    async def get_analytics_summary(
        self,
        user_id: Optional[uuid.UUID] = None,
        days: int = 30,
    ) -> Dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return await self.repo.get_summary_for_user(user_id=user_id, since=since)
