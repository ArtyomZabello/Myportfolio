"""Shared pytest fixtures for the Conduit test automation suite."""

from collections.abc import Generator, Iterator

import allure
import httpx
import pytest
from playwright.sync_api import Page

from ai_engine.gemini_analyzer import GeminiAnalyzer
from api_client.base_client import BaseAPIClient
from api_client.services.tags_service import TagsService
from config.settings import Config
from ui_pages.app import App


@pytest.fixture(scope="session")
def config() -> Config:
    """Provide session-scoped application configuration."""
    return Config()


@pytest.fixture(scope="session")
def api_client(config: Config) -> Generator[BaseAPIClient, None, None]:
    """Provide a session-scoped API client bound to the resolved configuration."""
    client = BaseAPIClient(config)
    yield client
    client.close()


@pytest.fixture(scope="session")
def tags_service(config: Config) -> Generator[TagsService, None, None]:
    """Provide a session-scoped tags service bound to the resolved configuration."""
    service = TagsService(config)
    yield service
    service.close()


@pytest.fixture
def ui_app(page: Page, config: Config) -> App:
    """Provide a function-scoped application facade bound to a Playwright page."""
    frontend_url = config.UI_BASE_URL.rstrip("/")

    try:
        httpx.get(frontend_url, timeout=config.API_TIMEOUT, follow_redirects=True)
    except httpx.HTTPError as exc:
        pytest.skip(f"Conduit frontend is not running at {frontend_url}: {exc}")

    page.goto(frontend_url)
    return App(page)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> Iterator[None]:
    """Attach AI-generated RCA summaries to Allure when a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed or call.excinfo is None:
        return

    error_trace = str(call.excinfo.value)
    analyzer = GeminiAnalyzer(Config())
    analysis = analyzer.analyze_failure(item.nodeid, error_trace)

    if analysis is not None:
        allure.attach(
            analysis,
            name="🤖 AI Root Cause Analysis",
            attachment_type=allure.attachment_type.TEXT,
        )
