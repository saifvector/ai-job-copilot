"""
Gemini AI Provider implementations for Resume Intelligence Engine.
Supports Gemini 2.5 Pro (Primary) and Gemini 2.5 Flash (Fallback).
"""
import json
import re
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

from core.ai.base import AIProvider
from core.config import settings
from core.exceptions import AIServiceException
from core.logging import get_logger

logger = get_logger("ai.gemini")


def clean_json_response(raw_text: str) -> str:
    """
    Ensures raw response text is valid JSON by trimming markdown wrappers or commentary.
    """
    text = raw_text.strip()
    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
    return text


class BaseGeminiProvider(AIProvider):
    """
    Base Google Gemini Provider using official google-genai SDK.
    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self._model_name = model
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._timeout = timeout or settings.AI_REQUEST_TIMEOUT
        self._client: Optional[genai.Client] = None

    @property
    def model_name(self) -> str:
        return self._model_name

    def _get_client(self) -> genai.Client:
        if not self._client:
            if not self._api_key or self._api_key.strip() == "":
                raise AIServiceException(
                    message="Gemini API Key is not configured. Please set GEMINI_API_KEY.",
                    details={"model": self._model_name},
                )
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    async def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
    ) -> str:
        """
        Invokes Gemini model to generate a strict RFC 8259 JSON response.
        """
        logger.info(
            "Dispatching JSON generation request to Gemini",
            extra={"model": self._model_name, "prompt_length": len(prompt)},
        )

        try:
            client = self._get_client()

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
                temperature=0.1,  # Low temperature to minimize hallucinations
            )

            response = await client.aio.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=config,
            )

            raw_text = response.text or ""
            cleaned_json = clean_json_response(raw_text)

            if not cleaned_json:
                raise AIServiceException(
                    message=f"Gemini model {self._model_name} returned an empty response.",
                    details={"model": self._model_name},
                )

            # Quick structural sanity check to confirm it can be parsed as JSON
            try:
                json.loads(cleaned_json)
            except json.JSONDecodeError as decode_err:
                logger.error(
                    "Invalid JSON returned from Gemini",
                    extra={"model": self._model_name, "raw_preview": raw_text[:200]},
                )
                raise AIServiceException(
                    message=f"Gemini model {self._model_name} produced invalid JSON syntax.",
                    details={"model": self._model_name, "error": str(decode_err)},
                )

            logger.info(
                "Gemini JSON generation succeeded",
                extra={"model": self._model_name, "response_length": len(cleaned_json)},
            )
            return cleaned_json

        except APIError as api_err:
            logger.error(
                "Gemini API Error encountered",
                extra={"model": self._model_name, "error": str(api_err)},
            )
            raise AIServiceException(
                message=f"Gemini API Error on {self._model_name}: {str(api_err)}",
                details={"model": self._model_name, "error": str(api_err)},
            )
        except AIServiceException:
            raise
        except Exception as exc:
            logger.error(
                "Unexpected failure calling Gemini",
                extra={"model": self._model_name, "error": str(exc)},
            )
            raise AIServiceException(
                message=f"Unexpected error calling Gemini model {self._model_name}: {str(exc)}",
                details={"model": self._model_name, "error": str(exc)},
            )


class GeminiProProvider(BaseGeminiProvider):
    """
    Primary Provider: Gemini 2.5 Pro.
    High-capacity reasoning model for comprehensive resume entity extraction.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            model=settings.GEMINI_PRIMARY_MODEL,
            api_key=api_key,
        )


class GeminiFlashProvider(BaseGeminiProvider):
    """
    Fallback Provider: Gemini 2.5 Flash.
    Ultra-fast, low-latency model for rapid fallback recovery.
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            model=settings.GEMINI_FALLBACK_MODEL,
            api_key=api_key,
        )
