"""
ReportRepository for Phase 9 Reporting & Export Center.
Provides persistence and query methods for generated reports, download metrics,
and storage accounting.
"""
import uuid
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.report import ReportModel
from repositories.base import BaseRepository


class ReportRepository(BaseRepository[ReportModel]):
    """
    Repository layer for managing Report entities in database.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ReportModel, session)

    async def create(self, data: Dict[str, Any]) -> ReportModel:
        """Create new Report entity."""
        report = ReportModel(**data)
        self.session.add(report)
        await self.session.flush()
        await self.session.refresh(report)
        return report

    async def findById(
        self,
        report_id: Union[uuid.UUID, str],
    ) -> Optional[ReportModel]:
        """Find report by ID."""
        r_id = uuid.UUID(str(report_id))
        stmt = select(ReportModel).where(ReportModel.id == r_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def findByUser(
        self,
        user_id: Union[uuid.UUID, str],
        report_type: Optional[str] = None,
        export_format: Optional[str] = None,
    ) -> List[ReportModel]:
        """Find reports for a user with optional filters, ordered by generated_at desc."""
        u_id = uuid.UUID(str(user_id))
        stmt = select(ReportModel).where(ReportModel.user_id == u_id)
        if report_type:
            stmt = stmt.where(ReportModel.report_type == report_type)
        if export_format:
            stmt = stmt.where(ReportModel.format == export_format.upper())
        stmt = stmt.order_by(desc(ReportModel.generated_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def incrementDownloadCount(
        self,
        report_id: Union[uuid.UUID, str],
    ) -> Optional[ReportModel]:
        """Increment download count of a report."""
        report = await self.findById(report_id)
        if report:
            report.download_count += 1
            self.session.add(report)
            await self.session.flush()
            await self.session.refresh(report)
        return report

    async def getStats(self, user_id: Union[uuid.UUID, str]) -> Dict[str, Any]:
        """Calculate aggregate report metrics for user."""
        u_id = uuid.UUID(str(user_id))
        stmt = select(
            func.count(ReportModel.id).label("total_reports"),
            func.coalesce(func.sum(ReportModel.download_count), 0).label("total_downloads"),
            func.coalesce(func.sum(ReportModel.file_size), 0).label("storage_used_bytes"),
        ).where(ReportModel.user_id == u_id)

        result = await self.session.execute(stmt)
        row = result.one()
        total_reports = int(row.total_reports or 0)
        total_downloads = int(row.total_downloads or 0)
        storage_used = int(row.storage_used_bytes or 0)

        # Most popular report type
        pop_stmt = (
            select(ReportModel.report_type, func.count(ReportModel.id).label("count"))
            .where(ReportModel.user_id == u_id)
            .group_by(ReportModel.report_type)
            .order_by(desc("count"))
            .limit(1)
        )
        pop_res = await self.session.execute(pop_stmt)
        pop_row = pop_res.first()
        most_popular = pop_row[0] if pop_row else None

        return {
            "total_reports": total_reports,
            "total_downloads": total_downloads,
            "storage_used_bytes": storage_used,
            "most_popular_type": most_popular,
        }

    async def delete(self, report_id: Union[uuid.UUID, str]) -> bool:
        """Delete report by ID."""
        r_id = uuid.UUID(str(report_id))
        report = await self.findById(r_id)
        if report:
            await self.session.delete(report)
            await self.session.flush()
            return True
        return False
