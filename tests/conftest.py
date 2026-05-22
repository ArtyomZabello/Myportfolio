"""Shared pytest fixtures for the Conduit test automation suite."""

from collections.abc import Generator

import allure
import httpx
import pytest
from playwright.sync_api import Page

from ai_engine.gemini_analyzer import GeminiAnalyzer
from api_client.services.articles_service import ArticlesService
from api_client.services.auth_service import AuthService
from api_client.services.comments_service import CommentsService
from api_client.services.tags_service import TagsService
from config.settings import Config
from data_factory.builders import ArticleDTO, UserDTO
from ui_pages.app import App


@pytest.fixture(scope="session")
def config() -> Config:
    """Provide session-scoped application configuration loaded from the environment."""
    return Config()


@pytest.fixture(scope="session")
def auth_service(config: Config) -> Generator[AuthService, None, None]:
    """Provide a session-scoped authentication service."""
    service = AuthService(config)
    yield service
    service.close()


@pytest.fixture(scope="session")
def articles_service(config: Config) -> Generator[ArticlesService, None, None]:
    """Provide a session-scoped articles service."""
    service = ArticlesService(config)
    yield service
    service.close()


@pytest.fixture(scope="session")
def comments_service(config: Config) -> Generator[CommentsService, None, None]:
    """Provide a session-scoped comments service."""
    service = CommentsService(config)
    yield service
    service.close()


@pytest.fixture(scope="session")
def tags_service(config: Config) -> Generator[TagsService, None, None]:
    """Provide a session-scoped tags service for typed tag endpoint access."""
    service = TagsService(config)
    yield service
    service.close()


@pytest.fixture
def authenticated_token(auth_service: AuthService) -> str:
    """Register a disposable user and return a bearer token for protected routes."""
    user = UserDTO.generate()

    with allure.step("Register disposable user for authenticated API tests"):
        response = auth_service.register(user)

    return response.user.token


@pytest.fixture
def created_article_slug(
    articles_service: ArticlesService,
    authenticated_token: str,
) -> str:
    """Create a disposable article and return its slug for downstream CRUD tests."""
    article = ArticleDTO.generate()

    with allure.step("Create disposable article for CRUD tests"):
        created = articles_service.create_article(authenticated_token, article)

    return created.article.slug


@pytest.fixture
def ui_app(page: Page, config: Config) -> App:
    """Provide a function-scoped UI facade after verifying the frontend is reachable.

    Skips the test when the Conduit frontend (or mock UI server) is not running.
    """
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
) -> Generator[None, pytest.CallInfo[None], None]:
    """Attach AI-generated RCA summaries to Allure when a test fails."""
    outcome: pytest.CallInfo[None] = yield
    report = outcome.get_result()  # type: ignore[attr-defined]

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
