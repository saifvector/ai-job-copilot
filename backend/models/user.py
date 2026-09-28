import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from models.profile import ProfileModel
    from models.resume import ResumeModel
    from models.skill import SkillModel
    from models.project import ProjectModel
    from models.education import EducationModel
    from models.experience import ExperienceModel
    from models.certification import CertificationModel
    from models.match_result import MatchResultModel
    from models.analytics_snapshot import AnalyticsSnapshotModel
    from models.tailored_resume import TailoredResumeModel
    from models.application import ApplicationModel
    from models.report import ReportModel
    from models.recruiter import RecruiterModel
    from models.interview_preparation import InterviewPreparationModel
    from models.mock_interview import MockInterviewModel
    from models.application_draft import ApplicationDraftModel
    from models.audit_log import AuditLogModel
    from models.api_key import ApiKeyModel
    from models.webhook import WebhookModel
    from models.oauth_connection import OAuthConnectionModel
    from models.agent_task import AgentTaskModel
    from models.agent_memory import AgentMemoryModel
    from models.workflow_execution import WorkflowExecutionModel
    from models.outcome_event import OutcomeEventModel
    from models.resume_performance import ResumePerformanceModel
    from models.skill_impact import SkillImpactModel
    from models.career_intelligence_snapshot import CareerIntelligenceSnapshotModel



class UserModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User database model representing account identity.
    Table: users (Prisma mapped)
    """
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # 1-to-1 Relationship with ProfileModel
    profile: Mapped[Optional["ProfileModel"]] = relationship(
        "ProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-1 Relationship with ResumeModel
    resume: Mapped[Optional["ResumeModel"]] = relationship(
        "ResumeModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-Many Relationships with Parsed Intelligence
    skills: Mapped[List["SkillModel"]] = relationship(
        "SkillModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    projects: Mapped[List["ProjectModel"]] = relationship(
        "ProjectModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    education: Mapped[List["EducationModel"]] = relationship(
        "EducationModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    experience: Mapped[List["ExperienceModel"]] = relationship(
        "ExperienceModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    certifications: Mapped[List["CertificationModel"]] = relationship(
        "CertificationModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-Many Relationship with MatchResultModel
    match_results: Mapped[List["MatchResultModel"]] = relationship(
        "MatchResultModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-Many Relationship with AnalyticsSnapshotModel
    analytics_snapshots: Mapped[List["AnalyticsSnapshotModel"]] = relationship(
        "AnalyticsSnapshotModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-Many Relationship with TailoredResumeModel
    tailored_resumes: Mapped[List["TailoredResumeModel"]] = relationship(
        "TailoredResumeModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-Many Relationship with ApplicationModel
    applications: Mapped[List["ApplicationModel"]] = relationship(
        "ApplicationModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # 1-to-Many Relationship with ReportModel
    reports: Mapped[List["ReportModel"]] = relationship(
        "ReportModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ReportModel.generated_at)",
    )

    # 1-to-Many Relationship with RecruiterModel (Phase 10 CRM)
    recruiters: Mapped[List["RecruiterModel"]] = relationship(
        "RecruiterModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(RecruiterModel.created_at)",
    )

    # 1-to-Many Relationship with InterviewPreparationModel (Phase 11 Interview Prep)
    interview_preparations: Mapped[List["InterviewPreparationModel"]] = relationship(
        "InterviewPreparationModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(InterviewPreparationModel.created_at)",
    )

    # 1-to-Many Relationship with MockInterviewModel (Phase 11 Interview Prep)
    mock_interviews: Mapped[List["MockInterviewModel"]] = relationship(
        "MockInterviewModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(MockInterviewModel.created_at)",
    )

    # 1-to-Many Relationship with ApplicationDraftModel (Phase 12 Application Assistant)
    application_drafts: Mapped[List["ApplicationDraftModel"]] = relationship(
        "ApplicationDraftModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ApplicationDraftModel.created_at)",
    )

    # 1-to-Many Relationship with AuditLogModel (Phase 13 Observability & Security)
    audit_logs: Mapped[List["AuditLogModel"]] = relationship(
        "AuditLogModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(AuditLogModel.created_at)",
    )

    # 1-to-Many Relationship with ApiKeyModel (Phase 14 Public API & Developer Portal)
    api_keys: Mapped[List["ApiKeyModel"]] = relationship(
        "ApiKeyModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ApiKeyModel.created_at)",
    )

    # 1-to-Many Relationship with WebhookModel (Phase 14 Webhooks)
    webhooks: Mapped[List["WebhookModel"]] = relationship(
        "WebhookModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(WebhookModel.created_at)",
    )

    # 1-to-Many Relationship with OAuthConnectionModel (Phase 14 Integrations)
    oauth_connections: Mapped[List["OAuthConnectionModel"]] = relationship(
        "OAuthConnectionModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(OAuthConnectionModel.created_at)",
    )

    # 1-to-Many Relationships with Phase 15 Agent Orchestration Models
    agent_tasks: Mapped[List["AgentTaskModel"]] = relationship(
        "AgentTaskModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(AgentTaskModel.created_at)",
    )

    agent_memories: Mapped[List["AgentMemoryModel"]] = relationship(
        "AgentMemoryModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(AgentMemoryModel.created_at)",
    )

    workflow_executions: Mapped[List["WorkflowExecutionModel"]] = relationship(
        "WorkflowExecutionModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(WorkflowExecutionModel.created_at)",
    )

    # 1-to-Many Relationships with Phase 16 Career Intelligence Models
    outcome_events: Mapped[List["OutcomeEventModel"]] = relationship(
        "OutcomeEventModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(OutcomeEventModel.occurred_at)",
    )

    resume_performances: Mapped[List["ResumePerformanceModel"]] = relationship(
        "ResumePerformanceModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(ResumePerformanceModel.response_rate)",
    )

    skill_impacts: Mapped[List["SkillImpactModel"]] = relationship(
        "SkillImpactModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(SkillImpactModel.interviews_influenced)",
    )

    career_intelligence_snapshots: Mapped[List["CareerIntelligenceSnapshotModel"]] = relationship(
        "CareerIntelligenceSnapshotModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(CareerIntelligenceSnapshotModel.snapshot_date)",
    )

    __table_args__ = (
        Index("idx_users_email", "email"),
    )

    def __repr__(self) -> str:
        return f"<UserModel id={self.id} email='{self.email}'>"
