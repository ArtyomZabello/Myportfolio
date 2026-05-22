"""Unit tests for AI RCA fail-safe behavior."""

from ai_engine.gemini_analyzer import GeminiAnalyzer
from config.settings import Config


def test_analyze_failure_returns_none_without_api_key() -> None:
    """Ensure missing GEMINI_API_KEY never breaks the test pipeline."""
    config = Config(GEMINI_API_KEY=None)
    analyzer = GeminiAnalyzer(config)

    result = analyzer.analyze_failure("tests/demo.py::test_demo", "AssertionError: boom")

    assert result is None


def test_analyze_failure_returns_none_with_empty_api_key() -> None:
    """Ensure an empty GEMINI_API_KEY is treated as disabled."""
    config = Config(GEMINI_API_KEY="")
    analyzer = GeminiAnalyzer(config)

    result = analyzer.analyze_failure("tests/demo.py::test_demo", "AssertionError: boom")

    assert result is None
