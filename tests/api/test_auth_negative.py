"""Negative authentication and authorization tests for the Conduit API."""

from __future__ import annotations

import allure
import pytest

from api_client.services.articles_service import ArticlesService
from api_client.services.auth_service import AuthService
from config.constants import (
    DEMO_INVALID_REGISTRATION_EMAIL,
    HTTP_CREATED,
    HTTP_UNAUTHORIZED,
    HTTP_UNPROCESSABLE,
)
from data_factory.builders import ArticleDTO


@pytest.mark.parametrize(
    ("credentials", "expected_status"),
    [
        pytest.param(
            {"email": "not-an-email", "password": "ValidPassword123!"},
            HTTP_UNPROCESSABLE,
            id="invalid-email-format",
        ),
        pytest.param(
            {"email": "missing@example.com", "password": ""},
            HTTP_UNPROCESSABLE,
            id="empty-password",
        ),
        pytest.param(
            {"email": "unknown@example.com", "password": "WrongPassword123!"},
            HTTP_UNAUTHORIZED,
            id="unknown-credentials",
        ),
    ],
)
@pytest.mark.security
@pytest.mark.regression
@allure.feature("Authentication")
@allure.story("Login")
@allure.title("POST /users/login rejects invalid credentials ({expected_status})")
def test_login_with_invalid_credentials(
    auth_service: AuthService,
    credentials: dict[str, str],
    expected_status: int,
) -> None:
    """Verify the login endpoint rejects malformed or incorrect credentials."""
    with allure.step("Attempt login with invalid credentials"):
        status_code = auth_service.login_raw(credentials)

    with allure.step("Verify API returns expected HTTP status"):
        assert status_code == expected_status


@pytest.mark.security
@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Authorization")
@allure.title("POST /articles without token returns 401 Unauthorized")
def test_create_article_without_token_returns_unauthorized(
    articles_service: ArticlesService,
) -> None:
    """Verify article creation is blocked when no authentication token is supplied."""
    article = ArticleDTO.generate()

    with allure.step("Attempt to create article without Authorization header"):
        status_code = articles_service.create_article_unauthenticated(article)

    with allure.step("Verify API rejects unauthenticated request"):
        assert status_code == HTTP_UNAUTHORIZED


@pytest.mark.demo
@allure.feature("Authentication")
@allure.story("Registration")
@allure.title("Intentional failure — invalid email registration (AI RCA demo)")
def test_intentional_failure_for_ai_analysis(auth_service: AuthService) -> None:
    """Demonstrate AI root cause analysis on a deliberately failing assertion.

    Excluded from the default CI pipeline via ``-m "not demo"``.
    """
    payload = {
        "user": {
            "username": "invaliduser",
            "email": DEMO_INVALID_REGISTRATION_EMAIL,
            "password": "ValidPassword123!",
        }
    }

    with allure.step("Submit registration request with invalid email"):
        status_code = auth_service.register_raw(payload)

    with allure.step("Verify registration succeeds (intentional failure)"):
        assert status_code == HTTP_CREATED
