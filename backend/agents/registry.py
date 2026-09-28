import logging
from typing import Any, Dict, List, Optional
from agents.base import BaseAgent
from agents.resume_agent import ResumeAgent
from agents.job_discovery_agent import JobDiscoveryAgent
from agents.matching_agent import MatchingAgent
from agents.analytics_agent import AnalyticsAgent
from agents.reporting_agent import ReportingAgent
from agents.interview_agent import InterviewAgent
from agents.recruiter_agent import RecruiterAgent
from agents.application_agent import ApplicationAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Central registry and locator for all specialized AI agents.
    Provides thread-safe access, metadata inspection, and dynamic agent lifecycle tracking.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        defaults = [
            ResumeAgent(),
            JobDiscoveryAgent(),
            MatchingAgent(),
            AnalyticsAgent(),
            ReportingAgent(),
            InterviewAgent(),
            RecruiterAgent(),
            ApplicationAgent(),
        ]
        for agent in defaults:
            self.register(agent)

    def register(self, agent: BaseAgent) -> None:
        canonical_name = agent.agent_name
        self._agents[canonical_name] = agent
        logger.debug(f"[AgentRegistry] Registered agent: {canonical_name}")

    def get(self, name: str) -> Optional[BaseAgent]:
        """Case-insensitive agent lookup."""
        if not name:
            return None
        # Exact match first
        if name in self._agents:
            return self._agents[name]
        # Case-insensitive search
        lower_name = name.lower()
        for k, v in self._agents.items():
            if k.lower() == lower_name:
                return v
        return None

    def has(self, name: str) -> bool:
        return self.get(name) is not None

    def list_agents(self) -> List[Dict[str, Any]]:
        """Returns structured metadata for all registered agents."""
        agent_list = []
        for agent in self._agents.values():
            agent_list.append({
                "name": agent.agent_name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "default_model": agent.default_model,
                "status": agent.status,
            })
        return agent_list


# Global Singleton Instance
agent_registry = AgentRegistry()
