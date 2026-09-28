import uuid
from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from core.logging import correlation_id_ctx
from core.storage.base import StorageProvider
from core.storage.factory import get_storage_provider
from repositories.candidate_intelligence_repository import (
    CertificationRepository,
    EducationRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from repositories.job_repository import JobRepository
from repositories.match_repository import MatchRepository
from repositories.analytics_repository import AnalyticsRepository
from repositories.tailored_resume_repository import TailoredResumeRepository
from repositories.application_repository import ApplicationRepository
from repositories.application_event_repository import ApplicationEventRepository
from repositories.interview_repository import (
    InterviewRepository,
    InterviewPreparationRepository,
    QuestionRepository,
    MockInterviewRepository,
)
from repositories.report_repository import ReportRepository
from repositories.recruiter_repository import RecruiterRepository
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from repositories.user_repository import UserRepository
from services.job_service import JobService
from services.matching_service import MatchingService
from services.analytics_service import AnalyticsService
from services.profile_service import ProfileService
from services.resume_parser_service import ResumeParserService
from services.resume_service import ResumeService
from services.resume_tailoring_service import ResumeTailoringService
from repositories.application_assistant_repository import (
    ApplicationDraftRepository,
    ApplicationQuestionRepository,
)
from services.application_service import ApplicationService
from services.application_assistant_service import ApplicationAssistantService
from services.report_service import ReportService
from services.recruiter_service import RecruiterService
from services.interview_service import InterviewService
from services.user_service import UserService
from repositories.audit_log_repository import AuditLogRepository
from services.audit_log_service import AuditLogService
from services.database_health_service import DatabaseHealthService
from services.backup_service import BackupService
from services.monitoring_service import MonitoringService
from services.ai_cost_service import AICostService, ai_cost_service
from core.cache import RedisCacheManager, cache_manager
from core.security.tokens import TokenService
from workers.task_queue import BackgroundTaskQueue, task_queue

DEFAULT_DEMO_USER_ID = uuid.UUID("a0000000-0000-0000-0000-000000000001")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding active async database session."""
    async for session in get_db_session():
        yield session


def get_correlation_id(request: Request) -> str:
    """Dependency providing current request correlation ID."""
    cid = correlation_id_ctx.get()
    if not cid:
        cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    return cid


def get_current_user_id(request: Request) -> uuid.UUID:
    """
    Resolve active user identity for request.
    Extracts from X-User-Id header or user_id query parameter,
    falling back to the initial demo user UUID.
    """
    user_header = request.headers.get("X-User-Id")
    if user_header:
        try:
            return uuid.UUID(user_header)
        except ValueError:
            pass

    query_user = request.query_params.get("user_id")
    if query_user:
        try:
            return uuid.UUID(query_user)
        except ValueError:
            pass

    return DEFAULT_DEMO_USER_ID


def get_storage() -> StorageProvider:
    """Dependency injecting configured StorageProvider."""
    return get_storage_provider()


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency injecting UserRepository."""
    return UserRepository(session=session)


def get_profile_repository(session: AsyncSession = Depends(get_db)) -> ProfileRepository:
    """Dependency injecting ProfileRepository."""
    return ProfileRepository(session=session)


def get_resume_repository(session: AsyncSession = Depends(get_db)) -> ResumeRepository:
    """Dependency injecting ResumeRepository."""
    return ResumeRepository(session=session)


def get_skill_repository(session: AsyncSession = Depends(get_db)) -> SkillRepository:
    """Dependency injecting SkillRepository."""
    return SkillRepository(session=session)


def get_project_repository(session: AsyncSession = Depends(get_db)) -> ProjectRepository:
    """Dependency injecting ProjectRepository."""
    return ProjectRepository(session=session)


def get_education_repository(session: AsyncSession = Depends(get_db)) -> EducationRepository:
    """Dependency injecting EducationRepository."""
    return EducationRepository(session=session)


def get_experience_repository(session: AsyncSession = Depends(get_db)) -> ExperienceRepository:
    """Dependency injecting ExperienceRepository."""
    return ExperienceRepository(session=session)


def get_certification_repository(session: AsyncSession = Depends(get_db)) -> CertificationRepository:
    """Dependency injecting CertificationRepository."""
    return CertificationRepository(session=session)


def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """Dependency injecting UserService."""
    return UserService(user_repo=user_repo)


def get_profile_service(
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ProfileService:
    """Dependency injecting ProfileService."""
    return ProfileService(profile_repo=profile_repo, user_repo=user_repo)


def get_resume_service(
    resume_repo: ResumeRepository = Depends(get_resume_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    storage_provider: StorageProvider = Depends(get_storage),
) -> ResumeService:
    """Dependency injecting ResumeService."""
    return ResumeService(
        resume_repo=resume_repo,
        profile_repo=profile_repo,
        storage_provider=storage_provider,
    )


def get_resume_parser_service(
    session: AsyncSession = Depends(get_db),
    storage_provider: StorageProvider = Depends(get_storage),
) -> ResumeParserService:
    """Dependency injecting ResumeParserService."""
    return ResumeParserService(session=session, storage_provider=storage_provider)


def get_job_service(
    session: AsyncSession = Depends(get_db),
) -> JobService:
    """Dependency injecting JobService for Job Discovery & Ingestion."""
    return JobService(session=session)


def get_job_repository(session: AsyncSession = Depends(get_db)) -> JobRepository:
    """Dependency injecting JobRepository."""
    return JobRepository(session=session)


def get_match_repository(session: AsyncSession = Depends(get_db)) -> MatchRepository:
    """Dependency injecting MatchRepository."""
    return MatchRepository(session=session)


def get_matching_service(
    match_repo: MatchRepository = Depends(get_match_repository),
    job_repo: JobRepository = Depends(get_job_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    skill_repo: SkillRepository = Depends(get_skill_repository),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
    education_repo: EducationRepository = Depends(get_education_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
) -> MatchingService:
    """Dependency injecting MatchingService."""
    return MatchingService(
        match_repo=match_repo,
        job_repo=job_repo,
        user_repo=user_repo,
        profile_repo=profile_repo,
        skill_repo=skill_repo,
        experience_repo=experience_repo,
        education_repo=education_repo,
        project_repo=project_repo,
    )


def get_analytics_repository(session: AsyncSession = Depends(get_db)) -> AnalyticsRepository:
    """Dependency injecting AnalyticsRepository."""
    return AnalyticsRepository(session=session)


def get_analytics_service(
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    resume_repo: ResumeRepository = Depends(get_resume_repository),
    skill_repo: SkillRepository = Depends(get_skill_repository),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
    education_repo: EducationRepository = Depends(get_education_repository),
) -> AnalyticsService:
    """Dependency injecting AnalyticsService."""
    return AnalyticsService(
        analytics_repo=analytics_repo,
        user_repo=user_repo,
        profile_repo=profile_repo,
        resume_repo=resume_repo,
        skill_repo=skill_repo,
        experience_repo=experience_repo,
        education_repo=education_repo,
    )


def get_tailored_resume_repository(session: AsyncSession = Depends(get_db)) -> TailoredResumeRepository:
    """Dependency injecting TailoredResumeRepository."""
    return TailoredResumeRepository(session=session)


def get_resume_tailoring_service(
    tailored_repo: TailoredResumeRepository = Depends(get_tailored_resume_repository),
    job_repo: JobRepository = Depends(get_job_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    resume_repo: ResumeRepository = Depends(get_resume_repository),
    skill_repo: SkillRepository = Depends(get_skill_repository),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
    education_repo: EducationRepository = Depends(get_education_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    certification_repo: CertificationRepository = Depends(get_certification_repository),
) -> ResumeTailoringService:
    """Dependency injecting ResumeTailoringService."""
    return ResumeTailoringService(
        tailored_repo=tailored_repo,
        job_repo=job_repo,
        user_repo=user_repo,
        profile_repo=profile_repo,
        resume_repo=resume_repo,
        skill_repo=skill_repo,
        experience_repo=experience_repo,
        education_repo=education_repo,
        project_repo=project_repo,
        certification_repo=certification_repo,
    )


def get_application_repository(session: AsyncSession = Depends(get_db)) -> ApplicationRepository:
    """Dependency injecting ApplicationRepository."""
    return ApplicationRepository(session=session)


def get_application_event_repository(session: AsyncSession = Depends(get_db)) -> ApplicationEventRepository:
    """Dependency injecting ApplicationEventRepository."""
    return ApplicationEventRepository(session=session)


def get_interview_repository(session: AsyncSession = Depends(get_db)) -> InterviewRepository:
    """Dependency injecting InterviewRepository."""
    return InterviewRepository(session=session)


def get_application_service(
    application_repo: ApplicationRepository = Depends(get_application_repository),
    event_repo: ApplicationEventRepository = Depends(get_application_event_repository),
    interview_repo: InterviewRepository = Depends(get_interview_repository),
    job_repo: JobRepository = Depends(get_job_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ApplicationService:
    """Dependency injecting ApplicationService."""
    return ApplicationService(
        application_repo=application_repo,
        event_repo=event_repo,
        interview_repo=interview_repo,
        job_repo=job_repo,
        user_repo=user_repo,
    )


def get_report_repository(session: AsyncSession = Depends(get_db)) -> ReportRepository:
    """Dependency injecting ReportRepository."""
    return ReportRepository(session=session)


def get_report_service(
    report_repo: ReportRepository = Depends(get_report_repository),
    session: AsyncSession = Depends(get_db),
) -> ReportService:
    """Dependency injecting ReportService."""
    return ReportService(report_repo=report_repo, session=session)


def get_recruiter_repository(session: AsyncSession = Depends(get_db)) -> RecruiterRepository:
    """Dependency injecting RecruiterRepository."""
    return RecruiterRepository(session=session)


def get_recruiter_service(
    recruiter_repo: RecruiterRepository = Depends(get_recruiter_repository),
) -> RecruiterService:
    """Dependency injecting RecruiterService."""
    return RecruiterService(recruiter_repo=recruiter_repo)


def get_interview_preparation_repository(
    session: AsyncSession = Depends(get_db),
) -> InterviewPreparationRepository:
    """Dependency injecting InterviewPreparationRepository."""
    return InterviewPreparationRepository(session=session)


def get_question_repository(
    session: AsyncSession = Depends(get_db),
) -> QuestionRepository:
    """Dependency injecting QuestionRepository."""
    return QuestionRepository(session=session)


def get_mock_interview_repository(
    session: AsyncSession = Depends(get_db),
) -> MockInterviewRepository:
    """Dependency injecting MockInterviewRepository."""
    return MockInterviewRepository(session=session)


def get_interview_service(
    prep_repo: InterviewPreparationRepository = Depends(get_interview_preparation_repository),
    question_repo: QuestionRepository = Depends(get_question_repository),
    mock_repo: MockInterviewRepository = Depends(get_mock_interview_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    job_repo: JobRepository = Depends(get_job_repository),
    skill_repo: SkillRepository = Depends(get_skill_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
) -> InterviewService:
    """Dependency injecting InterviewService."""
    return InterviewService(
        prep_repo=prep_repo,
        question_repo=question_repo,
        mock_repo=mock_repo,
        user_repo=user_repo,
        job_repo=job_repo,
        skill_repo=skill_repo,
        project_repo=project_repo,
        experience_repo=experience_repo,
    )


def get_application_draft_repository(
    session: AsyncSession = Depends(get_db),
) -> ApplicationDraftRepository:
    """Dependency injecting ApplicationDraftRepository."""
    return ApplicationDraftRepository(session=session)


def get_application_question_repository(
    session: AsyncSession = Depends(get_db),
) -> ApplicationQuestionRepository:
    """Dependency injecting ApplicationQuestionRepository."""
    return ApplicationQuestionRepository(session=session)


def get_application_assistant_service(
    draft_repo: ApplicationDraftRepository = Depends(get_application_draft_repository),
    question_repo: ApplicationQuestionRepository = Depends(get_application_question_repository),
    job_repo: JobRepository = Depends(get_job_repository),
    profile_repo: ProfileRepository = Depends(get_profile_repository),
    resume_repo: ResumeRepository = Depends(get_resume_repository),
    tailored_resume_repo: TailoredResumeRepository = Depends(get_tailored_resume_repository),
    skill_repo: SkillRepository = Depends(get_skill_repository),
    experience_repo: ExperienceRepository = Depends(get_experience_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    education_repo: EducationRepository = Depends(get_education_repository),
) -> ApplicationAssistantService:
    """Dependency injecting ApplicationAssistantService."""
    return ApplicationAssistantService(
        draft_repo=draft_repo,
        question_repo=question_repo,
        job_repo=job_repo,
        profile_repo=profile_repo,
        resume_repo=resume_repo,
        tailored_resume_repo=tailored_resume_repo,
        skill_repo=skill_repo,
        experience_repo=experience_repo,
        project_repo=project_repo,
        education_repo=education_repo,
    )


def get_audit_log_repository(
    session: AsyncSession = Depends(get_db),
) -> AuditLogRepository:
    """Dependency injecting AuditLogRepository."""
    return AuditLogRepository(session=session)


def get_audit_log_service(
    session: AsyncSession = Depends(get_db),
) -> AuditLogService:
    """Dependency injecting AuditLogService."""
    return AuditLogService(session=session)


def get_database_health_service(
    session: AsyncSession = Depends(get_db),
) -> DatabaseHealthService:
    """Dependency injecting DatabaseHealthService."""
    return DatabaseHealthService(session=session)


def get_backup_service() -> BackupService:
    """Dependency injecting BackupService."""
    return BackupService()


def get_monitoring_service() -> MonitoringService:
    """Dependency injecting MonitoringService."""
    return MonitoringService()


def get_ai_cost_service() -> AICostService:
    """Dependency injecting AICostService."""
    return ai_cost_service


def get_cache() -> RedisCacheManager:
    """Dependency injecting RedisCacheManager."""
    return cache_manager


def get_task_queue() -> BackgroundTaskQueue:
    """Dependency injecting BackgroundTaskQueue."""
    return task_queue


def get_authenticated_user_id(request: Request) -> uuid.UUID:
    """
    Extracts authenticated user ID from Authorization: Bearer <jwt> header,
    with fallback to X-User-Id / query parameter / default demo user.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        try:
            payload = TokenService.verify_token(token, expected_type="access")
            sub = payload.get("sub")
            if sub:
                return uuid.UUID(sub)
        except Exception:
            pass

    return get_current_user_id(request)
