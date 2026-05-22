"""Gemini-powered root cause analysis for automated test failures."""

from __future__ import annotations

import logging
from typing import Any, Final

import httpx

from config.settings import Config

logger = logging.getLogger(__name__)

_GEMINI_ENDPOINT: Final[str] = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)


class GeminiAnalyzer:
    """Fail-safe analyzer that requests concise RCA summaries from Gemini."""

    def __init__(self, config: Config) -> None:
        """Initialize the analyzer with environment-driven configuration.

        Args:
            config: Application settings containing the optional Gemini API key.
        """
        self._config = config
        self._api_key = config.GEMINI_API_KEY

    def analyze_failure(self, test_name: str, error_trace: str) -> str | None:
        """Request a concise root cause summary for a failed test.

        Args:
            test_name: Pytest node identifier for the failing test.
            error_trace: String representation of the raised exception.

        Returns:
            A short RCA summary when available, otherwise ``None``.
        """
        if not self._api_key:
            return None

        prompt = (
            "You are a Senior SDET. Analyze this test failure and provide a root cause "
            f"in 1-2 short sentences. Test: {test_name}. Error: {error_trace}."
        )
        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                },
            ],
        }

        try:
            with httpx.Client(timeout=self._config.API_TIMEOUT) as client:
                response = client.post(
                    _GEMINI_ENDPOINT,
                    params={"key": self._api_key},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            logger.warning("Gemini RCA request failed: %s", exc)
            return None
        except ValueError as exc:
            logger.warning("Gemini RCA response parsing failed: %s", exc)
            return None

        return self._extract_analysis(body)

    def _extract_analysis(self, body: dict[str, Any]) -> str | None:
        """Extract the generated RCA text from a Gemini API response payload."""
        try:
            candidates = body["candidates"]
            content = candidates[0]["content"]
            parts = content["parts"]
            text = parts[0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            logger.warning("Unexpected Gemini RCA response shape: %s", exc)
            return None

        if not isinstance(text, str) or not text.strip():
            return None

        return text.strip()
