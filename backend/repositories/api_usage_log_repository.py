import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.api_usage_log import ApiUsageLogModel
from repositories.base import BaseRepository


class ApiUsageLogRepository(BaseRepository[ApiUsageLogModel]):
    """
    Repository for storing and aggregating API analytics and telemetry.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(model=ApiUsageLogModel, session=session)

    async def log_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency_ms: float,
        user_id: Optional[uuid.UUID] = None,
        api_key_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
    ) -> ApiUsageLogModel:
        entry = ApiUsageLogModel(
            user_id=user_id,
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            ip_address=ip_address,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def get_summary_for_user(
        self,
        user_id: Optional[uuid.UUID] = None,
        since: Optional[datetime] = None,
    ) -> Dict:
        """Computes aggregate analytics: total requests, error rate, avg latency, and endpoint breakdown."""
        query = select(ApiUsageLogModel)
        if user_id:
            query = query.where(ApiUsageLogModel.user_id == user_id)
        if since:
            query = query.where(ApiUsageLogModel.created_at >= since)

        res = await self.session.execute(query)
        logs = res.scalars().all()

        total_requests = len(logs)
        if total_requests == 0:
            return {
                "total_requests": 0,
                "total_errors": 0,
                "error_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "endpoints": [],
            }

        errors = [l for l in logs if l.status_code >= 400]
        total_errors = len(errors)
        error_rate = round((total_errors / total_requests) * 100, 2)
        latencies = sorted([l.latency_ms for l in logs])
        avg_latency_ms = round(sum(latencies) / total_requests, 2)
        p95_idx = int(len(latencies) * 0.95)
        p95_latency_ms = round(latencies[min(p95_idx, len(latencies) - 1)], 2)

        # Aggregate by endpoint
        by_endpoint: Dict[str, Dict] = {}
        for l in logs:
            key = f"{l.method} {l.endpoint}"
            if key not in by_endpoint:
                by_endpoint[key] = {
                    "endpoint": l.endpoint,
                    "method": l.method,
                    "requests": 0,
                    "errors": 0,
                    "latencies": [],
                }
            by_endpoint[key]["requests"] += 1
            if l.status_code >= 400:
                by_endpoint[key]["errors"] += 1
            by_endpoint[key]["latencies"].append(l.latency_ms)

        endpoint_breakdowns = []
        for key, data in by_endpoint.items():
            reqs = data["requests"]
            errs = data["errors"]
            avg_lat = round(sum(data["latencies"]) / reqs, 2) if reqs > 0 else 0.0
            endpoint_breakdowns.append({
                "endpoint": data["endpoint"],
                "method": data["method"],
                "request_count": reqs,
                "error_count": errs,
                "error_rate": round((errs / reqs) * 100, 2) if reqs > 0 else 0.0,
                "avg_latency_ms": avg_lat,
            })

        endpoint_breakdowns.sort(key=lambda x: x["request_count"], reverse=True)

        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency_ms,
            "p95_latency_ms": p95_latency_ms,
            "endpoints": endpoint_breakdowns,
        }
