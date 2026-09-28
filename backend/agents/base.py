import abc
import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from orchestration.event_bus import AgentEvent, event_bus
from orchestration.model_router import model_router

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """
    Abstract Base Class for all specialized AI agents in AI Job Copilot.
    Provides execution lifecycle, context resolution, model routing, event emission,
    and structured output guarantees.
    """

    def __init__(self) -> None:
        self._status: str = "IDLE"

    @property
    @abc.abstractmethod
    def agent_name(self) -> str:
        """Unique agent identifier name (e.g. ResumeAgent)."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Domain description of this agent's platform role."""
        pass

    @property
    @abc.abstractmethod
    def capabilities(self) -> List[str]:
        """List of specific functional capabilities provided."""
        pass

    @property
    def default_model(self) -> str:
        """Default LLM model selected for this agent's domain."""
        return "gemini-2.5-flash"

    @property
    def status(self) -> str:
        return self._status

    async def execute(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None,
        session: Optional[AsyncSession] = None,
        model_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Public entrypoint for executing the agent.
        Orchestrates model selection, performance measurement, and event bus publishing.
        """
        self._status = "BUSY"
        start_time = time.perf_counter()
        shared_ctx = context if context is not None else {}

        # 1. Resolve LLM Model via Router
        routed = model_router.route(
            task_type=self.agent_name.lower(),
            model_override=model_override,
        )
        selected_model = routed["selected_model"]

        try:
            logger.info(f"[{self.agent_name}] Executing task with model={selected_model} (user_id={user_id})")

            # 2. Run Domain Specific Execution Logic
            result = await self._execute_internal(
                payload=payload,
                context=shared_ctx,
                user_id=user_id,
                session=session,
                model_used=selected_model,
            )

            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self._status = "IDLE"

            # 3. Publish Agent Event
            await event_bus.publish(
                AgentEvent(
                    event_name=f"{self.agent_name}Executed",
                    user_id=user_id,
                    payload={
                        "agent": self.agent_name,
                        "duration_ms": duration_ms,
                        "model_used": selected_model,
                        "status": "COMPLETED",
                    },
                )
            )

            return {
                "agent": self.agent_name,
                "status": "COMPLETED",
                "result": result,
                "model_used": selected_model,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            self._status = "IDLE"
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(f"[{self.agent_name}] Execution failed: {e}", exc_info=True)

            await event_bus.publish(
                AgentEvent(
                    event_name=f"{self.agent_name}Failed",
                    user_id=user_id,
                    payload={
                        "agent": self.agent_name,
                        "duration_ms": duration_ms,
                        "error": str(e),
                        "status": "FAILED",
                    },
                )
            )

            raise

    @abc.abstractmethod
    async def _execute_internal(
        self,
        payload: Dict[str, Any],
        context: Dict[str, Any],
        user_id: Optional[uuid.UUID],
        session: Optional[AsyncSession],
        model_used: str,
    ) -> Dict[str, Any]:
        """
        Specialized agent domain logic. Implemented by concrete agent subclasses.
        """
        pass
