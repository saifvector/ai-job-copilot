"""
RecruiterRepository for Phase 10 Recruiter CRM and Networking Intelligence System.
Handles database access for recruiters, contact interactions, and referrals.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.recruiter import RecruiterModel
from models.referral import ReferralModel
from models.contact_interaction import ContactInteractionModel
from repositories.base import BaseRepository


class RecruiterRepository(BaseRepository[RecruiterModel]):
    """
    Repository layer for managing Recruiter, Referral, and ContactInteraction entities.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RecruiterModel, session)

    async def create(self, data: Dict[str, Any]) -> RecruiterModel:
        """Create a new Recruiter entity."""
        recruiter = RecruiterModel(**data)
        self.session.add(recruiter)
        await self.session.flush()
        found = await self.findById(recruiter.id, eager=True)
        return found or recruiter

    async def update(
        self,
        recruiter: RecruiterModel,
        data: Dict[str, Any],
    ) -> RecruiterModel:
        """Update existing Recruiter attributes."""
        for key, value in data.items():
            if hasattr(recruiter, key) and value is not None:
                setattr(recruiter, key, value)
        recruiter.updated_at = datetime.now(timezone.utc)
        self.session.add(recruiter)
        await self.session.flush()
        found = await self.findById(recruiter.id, eager=True)
        return found or recruiter

    async def findById(
        self,
        recruiter_id: Union[uuid.UUID, str],
        eager: bool = True,
    ) -> Optional[RecruiterModel]:
        """Find recruiter by ID, with optional eager loading of interactions and referrals."""
        r_id = uuid.UUID(str(recruiter_id))
        stmt = select(RecruiterModel).where(RecruiterModel.id == r_id)
        if eager:
            stmt = stmt.options(
                selectinload(RecruiterModel.interactions),
                selectinload(RecruiterModel.referrals),
            )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def findByUser(
        self,
        user_id: Union[uuid.UUID, str],
        company: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[RecruiterModel]:
        """Query recruiters for a specific user with optional search and filters."""
        u_id = uuid.UUID(str(user_id))
        stmt = (
            select(RecruiterModel)
            .where(RecruiterModel.user_id == u_id)
            .options(
                selectinload(RecruiterModel.interactions),
                selectinload(RecruiterModel.referrals),
            )
        )

        if company and company.strip():
            stmt = stmt.where(func.lower(RecruiterModel.company) == company.strip().lower())

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(RecruiterModel.name).ilike(term),
                    func.lower(RecruiterModel.company).ilike(term),
                    func.lower(RecruiterModel.title).ilike(term),
                    func.lower(RecruiterModel.notes).ilike(term),
                )
            )

        stmt = stmt.order_by(desc(RecruiterModel.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def countByUser(
        self,
        user_id: Union[uuid.UUID, str],
        company: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count recruiters matching query parameters for pagination."""
        u_id = uuid.UUID(str(user_id))
        stmt = select(func.count(RecruiterModel.id)).where(RecruiterModel.user_id == u_id)

        if company and company.strip():
            stmt = stmt.where(func.lower(RecruiterModel.company) == company.strip().lower())

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(RecruiterModel.name).ilike(term),
                    func.lower(RecruiterModel.company).ilike(term),
                    func.lower(RecruiterModel.title).ilike(term),
                    func.lower(RecruiterModel.notes).ilike(term),
                )
            )

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def delete(self, recruiter: RecruiterModel) -> bool:
        """Delete recruiter and cascade remove associated interactions and referrals."""
        await self.session.delete(recruiter)
        await self.session.flush()
        return True

    # ---------------------------------------------------------
    # Interactions
    # ---------------------------------------------------------

    async def addInteraction(self, data: Dict[str, Any]) -> ContactInteractionModel:
        """Create a new contact interaction record."""
        interaction = ContactInteractionModel(**data)
        self.session.add(interaction)
        await self.session.flush()
        await self.session.refresh(interaction)
        return interaction

    async def getInteractions(
        self,
        recruiter_id: Union[uuid.UUID, str],
    ) -> List[ContactInteractionModel]:
        """Fetch all chronological interactions for a recruiter."""
        r_id = uuid.UUID(str(recruiter_id))
        stmt = (
            select(ContactInteractionModel)
            .where(ContactInteractionModel.recruiter_id == r_id)
            .order_by(desc(ContactInteractionModel.interaction_date))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---------------------------------------------------------
    # Referrals
    # ---------------------------------------------------------

    async def addReferral(self, data: Dict[str, Any]) -> ReferralModel:
        """Create a new Referral record."""
        referral = ReferralModel(**data)
        self.session.add(referral)
        await self.session.flush()
        await self.session.refresh(referral)
        return referral

    async def updateReferral(
        self,
        referral: ReferralModel,
        data: Dict[str, Any],
    ) -> ReferralModel:
        """Update existing Referral attributes."""
        for key, value in data.items():
            if hasattr(referral, key) and value is not None:
                setattr(referral, key, value)
        referral.updated_at = datetime.now(timezone.utc)
        self.session.add(referral)
        await self.session.flush()
        await self.session.refresh(referral)
        return referral

    async def findReferralById(
        self,
        referral_id: Union[uuid.UUID, str],
    ) -> Optional[ReferralModel]:
        """Find referral by ID with recruiter relationship loaded."""
        ref_id = uuid.UUID(str(referral_id))
        stmt = (
            select(ReferralModel)
            .options(selectinload(ReferralModel.recruiter))
            .where(ReferralModel.id == ref_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def listReferrals(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        company: Optional[str] = None,
    ) -> List[ReferralModel]:
        """List referrals across candidate's recruiters with optional filters."""
        u_id = uuid.UUID(str(user_id))
        stmt = (
            select(ReferralModel)
            .join(RecruiterModel, ReferralModel.recruiter_id == RecruiterModel.id)
            .options(selectinload(ReferralModel.recruiter))
            .where(RecruiterModel.user_id == u_id)
        )

        if status and status.strip() and status != "ALL":
            stmt = stmt.where(func.lower(ReferralModel.status) == status.strip().lower())

        if company and company.strip():
            stmt = stmt.where(func.lower(ReferralModel.company) == company.strip().lower())

        stmt = stmt.order_by(desc(ReferralModel.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def deleteReferral(self, referral: ReferralModel) -> bool:
        """Delete referral record."""
        await self.session.delete(referral)
        await self.session.flush()
        return True

    # ---------------------------------------------------------
    # Auxiliary Queries & Aggregates
    # ---------------------------------------------------------

    async def getDistinctCompanies(self, user_id: Union[uuid.UUID, str]) -> List[str]:
        """Get list of distinct company names across user's recruiters."""
        u_id = uuid.UUID(str(user_id))
        stmt = (
            select(RecruiterModel.company)
            .where(RecruiterModel.user_id == u_id)
            .distinct()
            .order_by(RecruiterModel.company)
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all() if row[0]]
