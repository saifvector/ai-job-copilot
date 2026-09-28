import uuid
import pytest
from agents.base import BaseAgent
from agents.registry import agent_registry
from agents.resume_agent import ResumeAgent
from agents.job_discovery_agent import JobDiscoveryAgent
from agents.matching_agent import MatchingAgent
from agents.analytics_agent import AnalyticsAgent
from agents.reporting_agent import ReportingAgent
from agents.interview_agent import InterviewAgent
from agents.recruiter_agent import RecruiterAgent
from agents.application_agent import ApplicationAgent


@pytest.mark.asyncio
async def test_agent_registry_contains_all_specialized_agents():
    expected_agents = [
        "ResumeAgent",
        "JobDiscoveryAgent",
        "MatchingAgent",
        "AnalyticsAgent",
        "ReportingAgent",
        "InterviewAgent",
        "RecruiterAgent",
        "ApplicationAgent",
    ]
    for name in expected_agents:
        assert agent_registry.has(name)
        agent = agent_registry.get(name)
        assert agent is not None
        assert agent.agent_name.lower() == name.lower()
        assert len(agent.capabilities) > 0
        assert agent.description != ""

    # Test case-insensitive lookup
    assert agent_registry.get("resumeagent") is not None
    assert agent_registry.get("JOBDISCOVERYAGENT") is not None

    all_agents = agent_registry.list_agents()
    assert len(all_agents) >= 8


@pytest.mark.asyncio
async def test_resume_agent_execution():
    agent = ResumeAgent()
    context = {}
    payload = {
        "mode": "analyze",
        "target_role": "Backend Staff Engineer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Distributed Systems"],
    }
    res = await agent.execute(payload=payload, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "ResumeAgent"
    assert "ats_score" in res["result"]
    assert res["result"]["ats_score"] > 0
    assert "resume_skills" in context
    assert "candidate_target_role" in context
    assert context["candidate_target_role"] == "Backend Staff Engineer"


@pytest.mark.asyncio
async def test_job_discovery_agent_execution():
    agent = JobDiscoveryAgent()
    context = {"candidate_target_role": "Platform Engineer", "resume_skills": ["Python", "Kubernetes"]}
    payload = {"limit": 3}
    res = await agent.execute(payload=payload, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "JobDiscoveryAgent"
    assert res["result"]["total_found"] > 0
    assert len(res["result"]["jobs"]) <= 3
    assert "discovered_jobs" in context
    assert len(context["discovered_jobs"]) > 0


@pytest.mark.asyncio
async def test_matching_agent_execution():
    agent = MatchingAgent()
    context = {
        "resume_skills": ["Python", "FastAPI", "PostgreSQL", "Kafka"],
        "discovered_jobs": [
            {
                "id": str(uuid.uuid4()),
                "title": "Senior Backend Engineer",
                "company": "ScaleAI",
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "required_years": 4.0,
            }
        ],
    }
    res = await agent.execute(payload={}, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "MatchingAgent"
    assert len(res["result"]["matches"]) == 1
    top_match = res["result"]["top_match"]
    assert top_match is not None
    assert top_match["overall_score"] >= 80.0
    assert "matches" in context
    assert "top_match_id" in context


@pytest.mark.asyncio
async def test_analytics_agent_execution():
    agent = AnalyticsAgent()
    context = {
        "ats_score": 88.0,
        "best_fit_score": 92.0,
        "resume_skills": ["Python", "FastAPI"],
        "matches": [{"missing_skills": ["GraphQL", "Kafka"]}],
    }
    res = await agent.execute(payload={}, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "AnalyticsAgent"
    assert res["result"]["readiness_score"] > 80.0
    assert "GraphQL" in res["result"]["primary_skill_gaps"]
    assert "analytics_summary" in context


@pytest.mark.asyncio
async def test_reporting_agent_execution():
    agent = ReportingAgent()
    context = {
        "ats_score": 88.0,
        "readiness_score": 90.0,
        "matches": [{"title": "Senior AI Systems Architect"}],
        "skill_gaps": ["Kubernetes"],
    }
    res = await agent.execute(payload={"format": "json"}, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "ReportingAgent"
    assert "report_id" in res["result"]
    assert len(res["result"]["sections"]) >= 3
    assert "generated_report" in context


@pytest.mark.asyncio
async def test_interview_agent_execution():
    agent = InterviewAgent()
    context = {"candidate_target_role": "Distributed Systems Architect"}
    payload = {
        "type": "technical",
        "question": "How do you handle split-brain scenarios in Raft consensus?",
        "user_answer": "When network partitioning occurred, the majority partition maintained quorum while the minority partition rejected write requests, ensuring zero data inconsistency.",
    }
    res = await agent.execute(payload=payload, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "InterviewAgent"
    assert len(res["result"]["questions"]) >= 3
    assert res["result"]["evaluation"] is not None
    assert res["result"]["evaluation"]["response_score"] > 60.0


@pytest.mark.asyncio
async def test_recruiter_agent_execution():
    agent = RecruiterAgent()
    context = {"candidate_target_role": "Full Stack Engineer", "resume_skills": ["TypeScript", "Python"]}
    payload = {"company": "Linear"}
    res = await agent.execute(payload=payload, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "RecruiterAgent"
    assert len(res["result"]["identified_contacts"]) >= 2
    assert "cold_email_pitch" in res["result"]["outreach_templates"]
    assert "recruiter_leads" in context


@pytest.mark.asyncio
async def test_application_agent_execution():
    agent = ApplicationAgent()
    context = {
        "resume_skills": ["Python", "FastAPI", "PostgreSQL"],
        "discovered_jobs": [{"company": "Datadog", "title": "Senior Infrastructure Engineer"}],
    }
    payload = {}
    res = await agent.execute(payload=payload, context=context)

    assert res["status"] == "COMPLETED"
    assert res["agent"] == "ApplicationAgent"
    assert res["result"]["qa_score"] > 80.0
    assert len(res["result"]["answered_questions"]) >= 2
    assert "tailored_pitch" in res["result"]
    assert "application_draft" in context
