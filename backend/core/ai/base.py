from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """
    Abstract AI Provider Interface.
    Enables pluggable LLM backends (Gemini, OpenAI, Claude, Nemotron, Ollama)
    without modifying downstream parsing or business logic.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the specific model identifier (e.g., 'gemini-2.5-pro')."""
        pass

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Execute completion expecting a structured JSON string in response.
        Raises AIServiceException on rate limits, network failure, or API errors.
        """
        pass
