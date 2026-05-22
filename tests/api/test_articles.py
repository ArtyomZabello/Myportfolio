"""Positive tests for Conduit article-related API endpoints."""

from __future__ import annotations

import allure
import pytest

from api_client.exceptions import APIResponseError
from api_client.services.articles_service import ArticlesService
from config.constants import ARTICLE_NOT_FOUND_STATUSES
from data_factory.builders import ArticleDTO

PAGINATION_LIMIT = 2
PAGINATION_SCAN_MAX_PAGES = 10


@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Article listing")
@allure.title("GET /articles returns a paginated list of articles")
def test_get_articles_returns_list(articles_service: ArticlesService) -> None:
    """Verify the articles endpoint returns HTTP 200 with an articles collection."""
    with allure.step("Request global articles feed"):
        feed = articles_service.list_articles()

    with allure.step("Verify response structure"):
        assert isinstance(feed.articles, list)
        assert feed.articlesCount >= 0


@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Article listing")
@allure.title("GET /articles supports limit and offset pagination")
def test_get_articles_supports_pagination(
    articles_service: ArticlesService,
    authenticated_token: str,
) -> None:
    """Verify pagination returns distinct slices and surfaces created articles."""
    created_slugs: set[str] = set()

    with allure.step("Create three uniquely titled articles for pagination verification"):
        for _ in range(3):
            created = articles_service.create_article(authenticated_token, ArticleDTO.generate())
            created_slugs.add(created.article.slug)

    with allure.step("Request the first two paginated pages"):
        first_page = articles_service.list_articles(limit=PAGINATION_LIMIT, offset=0)
        second_page = articles_service.list_articles(
            limit=PAGINATION_LIMIT,
            offset=PAGINATION_LIMIT,
        )

    with allure.step("Verify page boundaries and non-overlapping slices"):
        assert len(first_page.articles) == PAGINATION_LIMIT

        first_slugs = {article.slug for article in first_page.articles}
        second_slugs = {article.slug for article in second_page.articles}
        assert first_slugs.isdisjoint(second_slugs)

        combined_slugs = first_slugs | second_slugs
        assert len(combined_slugs) >= 3

    with allure.step("Locate all created articles through paginated feed traversal"):
        seen_slugs: set[str] = set()
        found_created: set[str] = set()
        offset = 0

        for _ in range(PAGINATION_SCAN_MAX_PAGES):
            page = articles_service.list_articles(limit=PAGINATION_LIMIT, offset=offset)
            if not page.articles:
                break

            assert len(page.articles) <= PAGINATION_LIMIT

            page_slugs = {article.slug for article in page.articles}
            assert page_slugs.isdisjoint(seen_slugs)

            seen_slugs |= page_slugs
            found_created |= page_slugs & created_slugs
            offset += PAGINATION_LIMIT

            if found_created == created_slugs:
                break

        assert found_created == created_slugs


@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Article creation")
@allure.title("POST /articles creates an article for an authenticated user")
def test_create_article_as_authenticated_user(
    articles_service: ArticlesService,
    authenticated_token: str,
) -> None:
    """Verify an authorized user can publish a new article."""
    article = ArticleDTO.generate()

    with allure.step("Submit new article with bearer token"):
        created = articles_service.create_article(authenticated_token, article)

    with allure.step("Verify article was created successfully"):
        assert created.article.title == article.title
        assert created.article.description == article.description
        assert created.article.body == article.body


@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Article retrieval")
@allure.title("GET /articles/{slug} returns a single article")
def test_get_article_by_slug(
    articles_service: ArticlesService,
    created_article_slug: str,
) -> None:
    """Verify a created article can be retrieved by slug."""
    with allure.step("Request article by slug"):
        article = articles_service.get_article(created_article_slug)

    with allure.step("Verify article payload is returned"):
        assert article.article.slug == created_article_slug


@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Article update")
@allure.title("PUT /articles/{slug} updates an existing article")
def test_update_article_by_slug(
    articles_service: ArticlesService,
    authenticated_token: str,
    created_article_slug: str,
) -> None:
    """Verify the article owner can update an existing article."""
    updated_article = ArticleDTO.generate()

    with allure.step("Submit article update with bearer token"):
        updated = articles_service.update_article(
            authenticated_token,
            created_article_slug,
            updated_article,
        )

    with allure.step("Verify article fields were updated"):
        assert updated.article.title == updated_article.title
        assert updated.article.description == updated_article.description
        assert updated.article.body == updated_article.body


@pytest.mark.regression
@allure.feature("Articles")
@allure.story("Article deletion")
@allure.title("DELETE /articles/{slug} removes an existing article")
def test_delete_article_by_slug(
    articles_service: ArticlesService,
    authenticated_token: str,
    created_article_slug: str,
) -> None:
    """Verify the article owner can delete an existing article."""
    with allure.step("Delete article by slug"):
        articles_service.delete_article(authenticated_token, created_article_slug)

    with allure.step("Verify deleted article is no longer retrievable"):
        try:
            articles_service.get_article(created_article_slug)
        except APIResponseError as exc:
            assert exc.status_code in ARTICLE_NOT_FOUND_STATUSES
        else:
            raise AssertionError(
                f"Expected deleted article lookup to fail with {ARTICLE_NOT_FOUND_STATUSES}",
            )
