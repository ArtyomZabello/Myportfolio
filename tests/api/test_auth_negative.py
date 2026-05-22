"""Negative authentication and authorization tests for the Conduit API."""

from __future__ import annotations

from typing import Any

import allure
import pytest

from api_client.base_client import BaseAPIClient
from data_factory.builders import ArticleDTO


@pytest.mark.parametrize(
    ("credentials", "expected_status"),
    [
        pytest.param(
            {"email": "not-an-email", "password": "ValidPassword123!"},
            422,
            id="invalid-email-format",
        ),
        pytest.param(
            {"email": "missing@example.com", "password": ""},
            422,
            id="empty-password",
        ),
        pytest.param(
            {"email": "unknown@example.com", "password": "WrongPassword123!"},
            401,
            id="unknown-credentials",
        ),
    ],
)
@allure.feature("Authentication")
@allure.story("Login")
@allure.title("POST /users/login rejects invalid credentials ({expected_status})")
def test_login_with_invalid_credentials(
    api_client: BaseAPIClient,
    credentials: dict[str, str],
    expected_status: int,
) -> None:
    """Verify the login endpoint rejects malformed or incorrect credentials."""
    with allure.step("Attempt login with invalid credentials"):
        response = api_client.post("/users/login", json={"user": credentials})

    with allure.step(f"Verify the API responds with HTTP {expected_status}"):
        assert response.status_code == expected_status, response.text


@allure.feature("Articles")
@allure.story("Authorization")
@allure.title("POST /articles without token returns 401 Unauthorized")
def test_create_article_without_token_returns_unauthorized(
    api_client: BaseAPIClient,
) -> None:
    """Verify article creation is blocked when no authentication token is supplied."""
    article = ArticleDTO.generate()
    payload: dict[str, Any] = {
        "article": {
            "title": article.title,
            "description": article.description,
            "body": article.body,
            "tagList": article.tags,
        }
    }

    with allure.step("Attempt to create an article without Authorization header"):
        response = api_client.post("/articles", json=payload)

    with allure.step("Verify the API rejects the unauthenticated request"):
        assert response.status_code == 401, response.text


@allure.feature("Authentication")
@allure.story("Registration")
@allure.title("Intentional failure — invalid email registration (AI RCA demo)")
def test_intentional_failure_for_ai_analysis(api_client: BaseAPIClient) -> None:
    """Demonstrate AI root cause analysis on a deliberately failing assertion.

    Sends a registration request with an invalid email address and asserts
    HTTP 201 even though the backend is expected to return 422 Unprocessable Entity.
    """
    payload = {
        "user": {
            "username": "invaliduser",
            "email": "plainaddress",
            "password": "ValidPassword123!",
        }
    }

    with allure.step("Отправляем запрос на регистрацию с невалидным email"):
        response = api_client.post("/users", json=payload)

    with allure.step("Проверяем успешную регистрацию (намеренно упадет)"):
        assert response.status_code == 201
