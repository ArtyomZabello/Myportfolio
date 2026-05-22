"""Service layer for Conduit article API operations."""

from __future__ import annotations

import allure

from api_client.base_client import BaseAPIClient
from api_client.exceptions import APIResponseError
from api_client.headers import authorization_headers
from api_client.models.articles_models import ArticleResponse, ArticlesFeedResponse
from config.constants import API_PATH_ARTICLES, HTTP_CREATED, HTTP_OK, article_path
from data_factory.builders import ArticleDTO


class ArticlesService(BaseAPIClient):
    """Encapsulates article CRUD and feed endpoints with typed responses."""

    def list_articles(self, *, limit: int = 10, offset: int = 0) -> ArticlesFeedResponse:
        """Retrieve a paginated global article feed."""
        endpoint = f"{API_PATH_ARTICLES}?limit={limit}&offset={offset}"
        with allure.step("Retrieve paginated article feed"):
            response = self._request("GET", endpoint)
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="GET",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return ArticlesFeedResponse.model_validate(response.json())

    def get_article(self, slug: str) -> ArticleResponse:
        """Retrieve a single article by slug."""
        endpoint = article_path(slug)
        with allure.step(f"Retrieve article '{slug}'"):
            response = self._request("GET", endpoint)
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="GET",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return ArticleResponse.model_validate(response.json())

    def create_article(self, token: str, article: ArticleDTO) -> ArticleResponse:
        """Create a new article as an authenticated user."""
        with allure.step("Create new article"):
            response = self._request(
                "POST",
                API_PATH_ARTICLES,
                json=article.to_create_payload(),
                headers=authorization_headers(token),
            )
            if response.status_code != HTTP_CREATED:
                raise APIResponseError(
                    method="POST",
                    endpoint=API_PATH_ARTICLES,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return ArticleResponse.model_validate(response.json())

    def update_article(self, token: str, slug: str, article: ArticleDTO) -> ArticleResponse:
        """Update an existing article owned by the authenticated user."""
        endpoint = article_path(slug)
        with allure.step(f"Update article '{slug}'"):
            response = self._request(
                "PUT",
                endpoint,
                json=article.to_update_payload(),
                headers=authorization_headers(token),
            )
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="PUT",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return ArticleResponse.model_validate(response.json())

    def delete_article(self, token: str, slug: str) -> None:
        """Delete an existing article owned by the authenticated user."""
        endpoint = article_path(slug)
        with allure.step(f"Delete article '{slug}'"):
            response = self._request("DELETE", endpoint, headers=authorization_headers(token))
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="DELETE",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )

    def create_article_unauthenticated(self, article: ArticleDTO) -> int:
        """Return the HTTP status code for an unauthenticated create attempt."""
        response = self._request("POST", API_PATH_ARTICLES, json=article.to_create_payload())
        return response.status_code
