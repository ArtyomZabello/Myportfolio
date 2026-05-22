"""Positive tests for Conduit article-related API endpoints."""

from __future__ import annotations

from typing import Any

import allure
import pytest

from api_client.base_client import BaseAPIClient
from data_factory.builders import ArticleDTO, UserDTO


def _article_payload(article: ArticleDTO) -> dict[str, Any]:
    """Map ``ArticleDTO`` fields to the RealWorld API request shape."""
    return {
        "title": article.title,
        "description": article.description,
        "body": article.body,
        "tagList": article.tags,
    }


@pytest.fixture
def authenticated_token(api_client: BaseAPIClient) -> str:
    """Register a fresh user and return a bearer token for authenticated requests."""
    user = UserDTO.generate()

    with allure.step("Register a new user for article tests"):
        response = api_client.post("/users", json={"user": user.model_dump()})
        assert response.status_code == 201, response.text
        token: str = response.json()["user"]["token"]

    return token


@allure.feature("Articles")
@allure.story("Article listing")
@allure.title("GET /articles returns a paginated list of articles")
def test_get_articles_returns_list(api_client: BaseAPIClient) -> None:
    """Verify the articles endpoint returns HTTP 200 with an articles collection."""
    with allure.step("Request the global articles feed"):
        response = api_client.get("/articles")

    with allure.step("Verify response status and payload structure"):
        assert response.status_code == 200
        payload = response.json()
        assert "articles" in payload
        assert isinstance(payload["articles"], list)
        assert "articlesCount" in payload
        assert isinstance(payload["articlesCount"], int)


@allure.feature("Articles")
@allure.story("Article creation")
@allure.title("POST /articles creates an article for an authenticated user")
def test_create_article_as_authenticated_user(
    api_client: BaseAPIClient,
    authenticated_token: str,
) -> None:
    """Verify an authorized user can publish a new article."""
    article = ArticleDTO.generate()

    with allure.step("Submit a new article with a valid bearer token"):
        response = api_client.post(
            "/articles",
            json={"article": _article_payload(article)},
            headers={"Authorization": f"Token {authenticated_token}"},
        )

    with allure.step("Verify the article was created successfully"):
        assert response.status_code == 201, response.text
        payload = response.json()
        assert "article" in payload
        created = payload["article"]
        assert created["title"] == article.title
        assert created["description"] == article.description
        assert created["body"] == article.body
