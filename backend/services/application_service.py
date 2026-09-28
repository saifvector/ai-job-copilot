"""
ApplicationService for Phase 8 Application Tracking System.
Orchestrates application pipeline tracking, status transitions, timeline events,
interview scheduling, and conversion analytics.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from core.exceptions import BadRequestException, NotFoundException
from models.application import ApplicationModel
from models.application_event import ApplicationEventModel
from models.interview import InterviewModel
from repositories.application_event_repository import ApplicationEventRepository
from repositories.application_repository import ApplicationRepository
from repositories.interview_repository import InterviewRepository
from repositories.job_repository import JobRepository
from repositories.user_repository import UserRepository
from schemas.application import (
    ApplicationAnalyticsResponse,
    ApplicationCreateRequest,
    ApplicationEventCreateRequest,
    ApplicationEventResponse,
    ApplicationJobSummary,
    ApplicationListItem,
    ApplicationResponse,
    InterviewCreateRequest,
    InterviewResponse,
    PipelineResponse,
)


class ApplicationService:
    """
    Business service layer managing candidate application lifecycle and pipeline analytics.
    """

    def __init__(
        self,
        application_repo: ApplicationRepository,
        event_repo: ApplicationEventRepository,
        interview_repo: InterviewRepository,
        job_repo: JobRepository,
        user_repo: UserRepository,
    ) -> None:
        self.application_repo = application_repo
        self.event_repo = event_repo
        self.interview_repo = interview_repo
        self.job_repo = job_repo
        self.user_repo = user_repo

    async def create_application(
        self,
        user_id: Union[uuid.UUID, str],
        request: ApplicationCreateRequest,
    ) -> ApplicationResponse:
        """
        Create a new job application or return existing if already tracked.
        Generates initial CREATED timeline event.
        """
        uid = uuid.UUID(str(user_id))
        user = await self.user_repo.get_by_id(uid)
        if not user:
            raise NotFoundException("User", str(uid))

        job = await self.job_repo.get_by_id(request.job_id)
        if not job:
            raise NotFoundException("Job", str(request.job_id))

        # Check if already tracked
        existing = await self.application_repo.findByUserAndJob(uid, request.job_id)
        if existing:
            # If exists and status requested differs, update status
            if request.status and existing.status != request.status:
                return await self.update_status(
                    existing.id,
                    request.status,
                    notes=f"Re-activated from {existing.status} to {request.status}",
                )
            return self._map_to_response(existing)

        now = datetime.now(timezone.utc)
        app_date = request.application_date
        if request.status == "APPLIED" and not app_date:
            app_date = now

        app_data: Dict[str, Any] = {
            "id": uuid.uuid4(),
            "user_id": uid,
            "job_id": request.job_id,
            "tailored_resume_id": request.tailored_resume_id,
            "status": request.status.upper(),
            "application_date": app_date,
            "last_updated": now,
            "source": request.source or job.source,
            "notes": request.notes,
            "created_at": now,
        }

        application = await self.application_repo.create(app_data)

        # Record initial creation event
        await self.event_repo.create({
            "id": uuid.uuid4(),
            "application_id": application.id,
            "event_type": "CREATED",
            "description": f"Application tracked for {job.title} at {job.company} as {application.status}.",
            "created_at": now,
        })

        if request.status == "APPLIED":
            await self.event_repo.create({
                "id": uuid.uuid4(),
                "application_id": application.id,
                "event_type": "STATUS_CHANGE",
                "description": f"Applied to {job.company} via {application.source or 'Direct'}.",
                "created_at": now,
            })

        # Reload with complete relations
        loaded = await self.application_repo.findById(application.id)
        return self._map_to_response(loaded or application)

    async def update_status(
        self,
        application_id: Union[uuid.UUID, str],
        new_status: str,
        notes: Optional[str] = None,
    ) -> ApplicationResponse:
        """
        Transition application pipeline status and record chronological event.
        """
        app = await self.application_repo.findById(application_id)
        if not app:
            raise NotFoundException("Application", str(application_id))

        status_normalized = new_status.upper()
        valid_statuses = {"SAVED", "APPLIED", "ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"}
        if status_normalized not in valid_statuses:
            raise BadRequestException(f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}")

        old_status = app.status
        now = datetime.now(timezone.utc)

        update_dict: Dict[str, Any] = {
            "status": status_normalized,
            "last_updated": now,
        }

        # Set application date if moving to APPLIED for the first time
        if status_normalized == "APPLIED" and not app.application_date:
            update_dict["application_date"] = now

        if notes:
            update_dict["notes"] = f"{app.notes}\n\n[Status Update: {status_normalized}]: {notes}" if app.notes else f"[Status Update: {status_normalized}]: {notes}"

        updated_app = await self.application_repo.update(app, update_dict)

        # Audit event
        event_desc = f"Status transitioned from {old_status} to {status_normalized}."
        if notes:
            event_desc += f" Note: {notes}"

        await self.event_repo.create({
            "id": uuid.uuid4(),
            "application_id": updated_app.id,
            "event_type": "STATUS_CHANGE",
            "description": event_desc,
            "created_at": now,
        })

        loaded = await self.application_repo.findById(updated_app.id)
        return self._map_to_response(loaded or updated_app)

    async def add_event(
        self,
        application_id: Union[uuid.UUID, str],
        request: ApplicationEventCreateRequest,
    ) -> ApplicationEventResponse:
        """Add custom timeline event or milestone."""
        app = await self.application_repo.findById(application_id)
        if not app:
            raise NotFoundException("Application", str(application_id))

        now = datetime.now(timezone.utc)
        event = await self.event_repo.create({
            "id": uuid.uuid4(),
            "application_id": app.id,
            "event_type": request.event_type.upper(),
            "description": request.description,
            "created_at": now,
        })

        await self.application_repo.update(app, {"last_updated": now})
        return ApplicationEventResponse.model_validate(event)

    async def add_interview(
        self,
        application_id: Union[uuid.UUID, str],
        request: InterviewCreateRequest,
    ) -> InterviewResponse:
        """
        Schedule an interview round, update status to INTERVIEW if appropriate,
        and log timeline event.
        """
        app = await self.application_repo.findById(application_id)
        if not app:
            raise NotFoundException("Application", str(application_id))

        now = datetime.now(timezone.utc)
        interview = await self.interview_repo.create({
            "id": uuid.uuid4(),
            "application_id": app.id,
            "interview_type": request.interview_type,
            "interview_date": request.interview_date,
            "interview_round": request.interview_round,
            "notes": request.notes,
            "created_at": now,
            "updated_at": now,
        })

        # Advance status to INTERVIEW if earlier in pipeline
        if app.status in {"SAVED", "APPLIED", "ASSESSMENT"}:
            await self.application_repo.update(app, {
                "status": "INTERVIEW",
                "last_updated": now,
            })

        # Timeline event
        date_str = request.interview_date.strftime("%b %d, %Y at %H:%M UTC")
        event_desc = f"Interview Scheduled: Round {request.interview_round} ({request.interview_type}) for {date_str}."
        if request.notes:
            event_desc += f" Notes: {request.notes}"

        await self.event_repo.create({
            "id": uuid.uuid4(),
            "application_id": app.id,
            "event_type": "INTERVIEW_SCHEDULED",
            "description": event_desc,
            "created_at": now,
        })

        return InterviewResponse.model_validate(interview)

    async def update_notes(
        self,
        application_id: Union[uuid.UUID, str],
        notes: str,
    ) -> ApplicationResponse:
        """Update candidate notes on an application."""
        app = await self.application_repo.findById(application_id)
        if not app:
            raise NotFoundException("Application", str(application_id))

        now = datetime.now(timezone.utc)
        updated_app = await self.application_repo.update(app, {
            "notes": notes,
            "last_updated": now,
        })

        await self.event_repo.create({
            "id": uuid.uuid4(),
            "application_id": app.id,
            "event_type": "NOTE_ADDED",
            "description": "Candidate updated application notes.",
            "created_at": now,
        })

        loaded = await self.application_repo.findById(updated_app.id)
        return self._map_to_response(loaded or updated_app)

    async def get_application_by_id(
        self,
        application_id: Union[uuid.UUID, str],
    ) -> ApplicationResponse:
        """Fetch single application with complete history."""
        app = await self.application_repo.findById(application_id)
        if not app:
            raise NotFoundException("Application", str(application_id))
        return self._map_to_response(app)

    async def list_applications(
        self,
        user_id: Union[uuid.UUID, str],
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[ApplicationListItem]:
        """List candidate applications with summary metadata."""
        apps = await self.application_repo.findByUser(user_id, status=status, limit=limit, skip=skip)
        return [self._map_to_list_item(a) for a in apps]

    async def get_pipeline(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> PipelineResponse:
        """
        Group candidate applications by status columns for the Kanban board view.
        """
        apps = await self.application_repo.getPipeline(user_id)
        pipeline = PipelineResponse()

        for app in apps:
            item = self._map_to_list_item(app)
            st = app.status.upper()
            if st == "SAVED":
                pipeline.saved.append(item)
            elif st == "APPLIED":
                pipeline.applied.append(item)
            elif st == "ASSESSMENT":
                pipeline.assessment.append(item)
            elif st == "INTERVIEW":
                pipeline.interview.append(item)
            elif st == "OFFER":
                pipeline.offer.append(item)
            elif st == "REJECTED":
                pipeline.rejected.append(item)
            elif st == "WITHDRAWN":
                pipeline.withdrawn.append(item)
            else:
                pipeline.saved.append(item)

        pipeline.total_applications = len(apps)
        pipeline.total_active = (
            len(pipeline.saved)
            + len(pipeline.applied)
            + len(pipeline.assessment)
            + len(pipeline.interview)
            + len(pipeline.offer)
        )
        return pipeline

    async def get_analytics(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> ApplicationAnalyticsResponse:
        """
        Calculate pipeline metrics, conversion rates, and monthly milestones.
        """
        uid = uuid.UUID(str(user_id))
        apps = await self.application_repo.getPipeline(uid)
        status_counts = await self.application_repo.getStatusCounts(uid)
        source_counts = await self.application_repo.getSourceCounts(uid)

        total_apps = len(apps)
        # Applications sent = status in [APPLIED, ASSESSMENT, INTERVIEW, OFFER, REJECTED, WITHDRAWN]
        sent_statuses = {"APPLIED", "ASSESSMENT", "INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"}
        apps_sent = sum(status_counts.get(s, 0) for s in sent_statuses)

        # Applications reaching interview = status in [INTERVIEW, OFFER] or having interviews
        interviews_received = status_counts.get("INTERVIEW", 0) + status_counts.get("OFFER", 0)
        offers_received = status_counts.get("OFFER", 0)
        rejections = status_counts.get("REJECTED", 0)

        # Responses received = any status past APPLIED
        responses_received = (
            status_counts.get("ASSESSMENT", 0)
            + status_counts.get("INTERVIEW", 0)
            + status_counts.get("OFFER", 0)
            + status_counts.get("REJECTED", 0)
        )

        response_rate = round((responses_received / apps_sent * 100), 1) if apps_sent > 0 else 0.0
        interview_rate = round((interviews_received / apps_sent * 100), 1) if apps_sent > 0 else 0.0
        offer_rate = round((offers_received / apps_sent * 100), 1) if apps_sent > 0 else 0.0

        # Upcoming interviews
        upcoming_interviews = await self.interview_repo.getUpcomingByUser(uid)

        # Applications this calendar month
        now = datetime.now(timezone.utc)
        current_year = now.year
        current_month = now.month
        apps_this_month = sum(
            1 for a in apps
            if (a.application_date and a.application_date.year == current_year and a.application_date.month == current_month)
            or (a.created_at.year == current_year and a.created_at.month == current_month)
        )

        return ApplicationAnalyticsResponse(
            total_applications=total_apps,
            applications_sent=apps_sent,
            interviews_received=interviews_received,
            offers_received=offers_received,
            rejections=rejections,
            response_rate=response_rate,
            interview_rate=interview_rate,
            offer_rate=offer_rate,
            by_status=status_counts,
            by_source=source_counts,
            interviews_scheduled_upcoming=len(upcoming_interviews),
            applications_this_month=apps_this_month,
        )

    async def delete_application(
        self,
        application_id: Union[uuid.UUID, str],
    ) -> bool:
        """Delete an application record and cascaded events."""
        app = await self.application_repo.findById(application_id)
        if not app:
            raise NotFoundException("Application", str(application_id))
        await self.application_repo.delete(app.id)
        return True

    def _map_to_response(self, app: ApplicationModel) -> ApplicationResponse:
        """Map ApplicationModel to typed ApplicationResponse with nested job summary."""
        job_summary = None
        if app.job:
            job_summary = ApplicationJobSummary(
                id=app.job.id,
                title=app.job.title,
                company=app.job.company,
                location=app.job.location,
                employment_type=app.job.employment_type,
                apply_url=app.job.apply_url,
                salary_min=app.job.salary_min,
                salary_max=app.job.salary_max,
                currency=app.job.currency or "USD",
            )

        events_list = [
            ApplicationEventResponse.model_validate(e)
            for e in (app.events or [])
        ]
        interviews_list = [
            InterviewResponse.model_validate(i)
            for i in (app.interviews or [])
        ]

        return ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            job_id=app.job_id,
            tailored_resume_id=app.tailored_resume_id,
            status=app.status,
            application_date=app.application_date,
            last_updated=app.last_updated,
            source=app.source,
            notes=app.notes,
            created_at=app.created_at,
            job=job_summary,
            events=events_list,
            interviews=interviews_list,
        )

    def _map_to_list_item(self, app: ApplicationModel) -> ApplicationListItem:
        """Map ApplicationModel to lightweight ApplicationListItem for Kanban board."""
        now = datetime.now(timezone.utc)
        next_interview = None
        if app.interviews:
            def _to_utc(dt: datetime) -> datetime:
                return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            future = [i.interview_date for i in app.interviews if _to_utc(i.interview_date) >= now]
            if future:
                next_interview = min(future)

        job_title = app.job.title if app.job else "Unknown Position"
        job_company = app.job.company if app.job else "Unknown Employer"
        job_location = app.job.location if app.job else "Remote"

        return ApplicationListItem(
            id=app.id,
            user_id=app.user_id,
            job_id=app.job_id,
            job_title=job_title,
            job_company=job_company,
            job_location=job_location,
            status=app.status,
            application_date=app.application_date,
            last_updated=app.last_updated,
            source=app.source,
            notes=app.notes,
            interview_count=len(app.interviews or []),
            next_interview_date=next_interview,
            tailored_resume_id=app.tailored_resume_id,
        )
