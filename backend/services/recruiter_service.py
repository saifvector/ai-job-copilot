"""
RecruiterService for Phase 10 Recruiter CRM and Networking Intelligence System.
Orchestrates recruiter contact management, interaction logs, referral pipelines,
and networking outreach analytics.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from models.recruiter import RecruiterModel
from models.referral import ReferralModel
from models.contact_interaction import ContactInteractionModel
from repositories.recruiter_repository import RecruiterRepository
from schemas.recruiter import (
    ContactInteractionCreateRequest,
    ContactInteractionResponse,
    NetworkingAnalyticsResponse,
    RecruiterCreateRequest,
    RecruiterDetailResponse,
    RecruiterListResponse,
    RecruiterResponse,
    RecruiterUpdateRequest,
    ReferralCreateRequest,
    ReferralResponse,
    ReferralUpdateRequest,
)


class RecruiterService:
    """
    High-level business service for Recruiter CRM, referral lifecycle, and networking analytics.
    """

    def __init__(self, recruiter_repo: RecruiterRepository) -> None:
        self.repo = recruiter_repo

    # ---------------------------------------------------------
    # Recruiter CRUD
    # ---------------------------------------------------------

    async def createRecruiter(
        self,
        user_id: Union[uuid.UUID, str],
        payload: RecruiterCreateRequest,
    ) -> RecruiterResponse:
        """Create a new recruiter or professional networking contact."""
        u_id = uuid.UUID(str(user_id))
        recruiter_data: Dict[str, Any] = {
            "user_id": u_id,
            "name": payload.name.strip(),
            "company": payload.company.strip(),
            "title": payload.title.strip() if payload.title else None,
            "email": payload.email.strip() if payload.email else None,
            "linkedin_url": payload.linkedin_url.strip() if payload.linkedin_url else None,
            "notes": payload.notes.strip() if payload.notes else None,
        }

        recruiter = await self.repo.create(recruiter_data)
        return self._map_to_response(recruiter)

    async def updateRecruiter(
        self,
        recruiter_id: Union[uuid.UUID, str],
        payload: RecruiterUpdateRequest,
    ) -> Optional[RecruiterResponse]:
        """Update existing recruiter details."""
        recruiter = await self.repo.findById(recruiter_id, eager=True)
        if not recruiter:
            return None

        update_data: Dict[str, Any] = {}
        if payload.name is not None:
            update_data["name"] = payload.name.strip()
        if payload.company is not None:
            update_data["company"] = payload.company.strip()
        if payload.title is not None:
            update_data["title"] = payload.title.strip() if payload.title else None
        if payload.email is not None:
            update_data["email"] = payload.email.strip() if payload.email else None
        if payload.linkedin_url is not None:
            update_data["linkedin_url"] = payload.linkedin_url.strip() if payload.linkedin_url else None
        if payload.notes is not None:
            update_data["notes"] = payload.notes.strip() if payload.notes else None

        updated = await self.repo.update(recruiter, update_data)
        return self._map_to_response(updated)

    async def getRecruiter(
        self,
        recruiter_id: Union[uuid.UUID, str],
    ) -> Optional[RecruiterDetailResponse]:
        """Fetch recruiter by ID with full interaction and referral history."""
        recruiter = await self.repo.findById(recruiter_id, eager=True)
        if not recruiter:
            return None
        return self._map_to_detail_response(recruiter)

    async def listRecruiters(
        self,
        user_id: Union[uuid.UUID, str],
        company: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> RecruiterListResponse:
        """List recruiters for a candidate with search, filtering, and summary statistics."""
        recruiters = await self.repo.findByUser(
            user_id=user_id,
            company=company,
            search=search,
            limit=limit,
            offset=offset,
        )
        total = await self.repo.countByUser(
            user_id=user_id,
            company=company,
            search=search,
        )
        companies = await self.repo.getDistinctCompanies(user_id=user_id)

        items = [self._map_to_response(r) for r in recruiters]
        return RecruiterListResponse(
            recruiters=items,
            total=total,
            companies=companies,
        )

    async def deleteRecruiter(
        self,
        recruiter_id: Union[uuid.UUID, str],
    ) -> bool:
        """Delete recruiter record and cascades."""
        recruiter = await self.repo.findById(recruiter_id, eager=False)
        if not recruiter:
            return False
        return await self.repo.delete(recruiter)

    # ---------------------------------------------------------
    # Interactions
    # ---------------------------------------------------------

    async def addInteraction(
        self,
        recruiter_id: Union[uuid.UUID, str],
        payload: ContactInteractionCreateRequest,
    ) -> Optional[ContactInteractionResponse]:
        """Record an outreach event (Message, Email, Referral, Call, Interview)."""
        recruiter = await self.repo.findById(recruiter_id, eager=False)
        if not recruiter:
            return None

        r_id = uuid.UUID(str(recruiter_id))
        interaction_date = payload.interaction_date or datetime.now(timezone.utc)

        data = {
            "recruiter_id": r_id,
            "interaction_type": payload.interaction_type,
            "summary": payload.summary.strip(),
            "interaction_date": interaction_date,
        }
        interaction = await self.repo.addInteraction(data)

        # Update recruiter timestamp to reflect latest touchpoint
        await self.repo.update(recruiter, {"updated_at": datetime.now(timezone.utc)})

        return ContactInteractionResponse.model_validate(interaction)

    async def getRecruiterHistory(
        self,
        recruiter_id: Union[uuid.UUID, str],
    ) -> List[ContactInteractionResponse]:
        """Retrieve chronological history of interactions for a recruiter."""
        interactions = await self.repo.getInteractions(recruiter_id)
        return [ContactInteractionResponse.model_validate(i) for i in interactions]

    # ---------------------------------------------------------
    # Referrals
    # ---------------------------------------------------------

    async def addReferral(
        self,
        recruiter_id: Union[uuid.UUID, str],
        payload: ReferralCreateRequest,
    ) -> Optional[ReferralResponse]:
        """Request or log a referral through a recruiter contact."""
        recruiter = await self.repo.findById(recruiter_id, eager=False)
        if not recruiter:
            return None

        r_id = uuid.UUID(str(recruiter_id))
        data = {
            "recruiter_id": r_id,
            "company": payload.company.strip(),
            "role": payload.role.strip(),
            "status": payload.status,
            "notes": payload.notes.strip() if payload.notes else None,
        }
        referral = await self.repo.addReferral(data)

        # Also automatically log a ContactInteraction of type 'Referral'
        interaction_summary = f"Referral {payload.status.lower()} for {payload.role} at {payload.company}."
        if payload.notes:
            interaction_summary += f" Notes: {payload.notes}"
        await self.repo.addInteraction({
            "recruiter_id": r_id,
            "interaction_type": "Referral",
            "summary": interaction_summary,
            "interaction_date": datetime.now(timezone.utc),
        })

        return self._map_to_referral_response(referral, recruiter.name)

    async def updateReferral(
        self,
        referral_id: Union[uuid.UUID, str],
        payload: ReferralUpdateRequest,
    ) -> Optional[ReferralResponse]:
        """Update referral status or role/company metadata."""
        referral = await self.repo.findReferralById(referral_id)
        if not referral:
            return None

        update_data: Dict[str, Any] = {}
        if payload.company is not None:
            update_data["company"] = payload.company.strip()
        if payload.role is not None:
            update_data["role"] = payload.role.strip()
        if payload.status is not None:
            update_data["status"] = payload.status
        if payload.notes is not None:
            update_data["notes"] = payload.notes.strip() if payload.notes else None

        updated = await self.repo.updateReferral(referral, update_data)
        recruiter_name = updated.recruiter.name if updated.recruiter else None
        return self._map_to_referral_response(updated, recruiter_name)

    async def listReferrals(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        company: Optional[str] = None,
    ) -> List[ReferralResponse]:
        """List all referrals for a user with optional status and company filters."""
        referrals = await self.repo.listReferrals(
            user_id=user_id,
            status=status,
            company=company,
        )
        return [
            self._map_to_referral_response(ref, ref.recruiter.name if ref.recruiter else None)
            for ref in referrals
        ]

    async def deleteReferral(
        self,
        referral_id: Union[uuid.UUID, str],
    ) -> bool:
        """Delete referral record."""
        referral = await self.repo.findReferralById(referral_id)
        if not referral:
            return False
        return await self.repo.deleteReferral(referral)

    # ---------------------------------------------------------
    # Analytics
    # ---------------------------------------------------------

    async def getNetworkingAnalytics(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> NetworkingAnalyticsResponse:
        """
        Calculate complete networking and outreach intelligence metrics:
        - Recruiters Contacted
        - Response Rate
        - Referral Success Rate
        - Companies Reached
        - Outreach Tracker metrics (Messages Sent, Responses Received, Referrals Requested, Referrals Received)
        """
        recruiters = await self.repo.findByUser(user_id=user_id, limit=1000)
        referrals = await self.repo.listReferrals(user_id=user_id)

        # 1. Recruiters Contacted: count recruiters with at least 1 interaction
        recruiters_contacted = 0
        companies_set = set()
        messages_sent = 0
        responses_received = 0
        interactions_by_type: Dict[str, int] = {
            "Message": 0,
            "Email": 0,
            "Referral": 0,
            "Call": 0,
            "Interview": 0,
        }

        for r in recruiters:
            if r.interactions and len(r.interactions) > 0:
                recruiters_contacted += 1
                companies_set.add(r.company.lower().strip())

            for i in r.interactions or []:
                itype = i.interaction_type
                if itype in interactions_by_type:
                    interactions_by_type[itype] += 1
                else:
                    interactions_by_type[itype] = 1

                if itype in ["Message", "Email"]:
                    messages_sent += 1
                elif itype in ["Call", "Interview"]:
                    responses_received += 1

        # Also count all companies in the network
        for r in recruiters:
            companies_set.add(r.company.lower().strip())
        companies_reached = len(companies_set)

        # 2. Referrals Analytics
        referrals_by_status: Dict[str, int] = {
            "Requested": 0,
            "Received": 0,
            "Declined": 0,
            "Pending": 0,
        }
        for ref in referrals:
            st = ref.status
            if st in referrals_by_status:
                referrals_by_status[st] += 1
            else:
                referrals_by_status[st] = 1

        referrals_requested = referrals_by_status.get("Requested", 0) + referrals_by_status.get("Pending", 0)
        referrals_received = referrals_by_status.get("Received", 0)
        total_referrals = len(referrals)

        # Response Rate = (responses_received / messages_sent) * 100
        # If interactions exist, response rate is computed; fallback to 0.0
        response_rate = 0.0
        if messages_sent > 0:
            response_rate = min(100.0, round((responses_received / messages_sent) * 100, 1))
        elif recruiters_contacted > 0 and responses_received > 0:
            response_rate = min(100.0, round((responses_received / recruiters_contacted) * 100, 1))

        # Referral Success Rate = (referrals_received / total_referrals) * 100
        referral_success_rate = 0.0
        if total_referrals > 0:
            referral_success_rate = round((referrals_received / total_referrals) * 100, 1)

        return NetworkingAnalyticsResponse(
            recruiters_contacted=recruiters_contacted,
            response_rate=response_rate,
            referral_success_rate=referral_success_rate,
            companies_reached=companies_reached,
            messages_sent=messages_sent,
            responses_received=responses_received,
            referrals_requested=referrals_requested if referrals_requested > 0 else total_referrals,
            referrals_received=referrals_received,
            interactions_by_type=interactions_by_type,
            referrals_by_status=referrals_by_status,
        )

    # ---------------------------------------------------------
    # Helper Mappers
    # ---------------------------------------------------------

    def _map_to_response(self, recruiter: RecruiterModel) -> RecruiterResponse:
        """Map SQLAlchemy RecruiterModel to Pydantic RecruiterResponse DTO."""
        interactions = recruiter.interactions or []
        last_date = interactions[0].interaction_date if interactions else None

        return RecruiterResponse(
            id=recruiter.id,
            user_id=recruiter.user_id,
            name=recruiter.name,
            company=recruiter.company,
            title=recruiter.title,
            email=recruiter.email,
            linkedin_url=recruiter.linkedin_url,
            notes=recruiter.notes,
            interaction_count=len(interactions),
            referral_count=len(recruiter.referrals or []),
            last_interaction_date=last_date,
            created_at=recruiter.created_at,
            updated_at=recruiter.updated_at,
        )

    def _map_to_detail_response(self, recruiter: RecruiterModel) -> RecruiterDetailResponse:
        """Map SQLAlchemy RecruiterModel to full RecruiterDetailResponse with history."""
        base_resp = self._map_to_response(recruiter)
        interactions = [
            ContactInteractionResponse.model_validate(i)
            for i in (recruiter.interactions or [])
        ]
        referrals = [
            self._map_to_referral_response(ref, recruiter.name)
            for ref in (recruiter.referrals or [])
        ]

        return RecruiterDetailResponse(
            **base_resp.model_dump(),
            interactions=interactions,
            referrals=referrals,
        )

    def _map_to_referral_response(
        self,
        referral: ReferralModel,
        recruiter_name: Optional[str] = None,
    ) -> ReferralResponse:
        """Map SQLAlchemy ReferralModel to Pydantic ReferralResponse DTO."""
        return ReferralResponse(
            id=referral.id,
            recruiter_id=referral.recruiter_id,
            company=referral.company,
            role=referral.role,
            status=referral.status,
            notes=referral.notes,
            created_at=referral.created_at,
            updated_at=referral.updated_at,
            recruiter_name=recruiter_name,
        )
