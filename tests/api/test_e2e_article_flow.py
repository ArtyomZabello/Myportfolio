"""End-to-end API flow covering auth, content creation, and verification."""

from __future__ import annotations

import allure
import pytest

from api_client.exceptions import APIResponseError
from api_client.services.articles_service import ArticlesService
from api_client.services.auth_service import AuthService
from api_client.services.comments_service import CommentsService
from config.constants import HTTP_NOT_FOUND
from data_factory.builders import ArticleDTO, CommentDTO, UserDTO


@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("User Journey")
@allure.story("Article lifecycle")
@allure.title("Complete API journey from registration to article cleanup")
def test_end_to_end_article_lifecycle(
    auth_service: AuthService,
    articles_service: ArticlesService,
    comments_service: CommentsService,
) -> None:
    """Verify register → login → article → comment → feed → delete across service layer."""
    user = UserDTO.generate()
    token = ""
    slug = ""
    comment_id = 0

    with allure.step("Register new user account"):
        registered = auth_service.register(user)
        token = registered.user.token

    with allure.step("Login with registered credentials"):
        logged_in = auth_service.login(email=user.email, password=user.password)
        token = logged_in.user.token

    with allure.step("Create article as authenticated user"):
        article = ArticleDTO.generate()
        created = articles_service.create_article(token, article)
        slug = created.article.slug

    with allure.step("Add comment to created article"):
        comment = CommentDTO.generate()
        created_comment = comments_service.create_comment(token, slug, comment)
        comment_id = created_comment.comment.id

    with allure.step("Verify article appears in global feed"):
        feed = articles_service.list_articles()
        feed_slugs = [item.slug for item in feed.articles]
        assert slug in feed_slugs

    with allure.step("Verify comment appears in article comments collection"):
        comments = comments_service.list_comments(slug)
        comment_ids = [item.id for item in comments.comments]
        assert comment_id in comment_ids

    with allure.step("Delete created article"):
        articles_service.delete_article(token, slug)

    with allure.step("Verify deleted article is absent from global feed"):
        final_feed = articles_service.list_articles()
        final_slugs = [item.slug for item in final_feed.articles]
        assert slug not in final_slugs

    with allure.step("Verify deleted article returns not found"):
        try:
            articles_service.get_article(slug)
        except APIResponseError as exc:
            assert exc.status_code == HTTP_NOT_FOUND
        else:
            raise AssertionError("Expected deleted article to return 404")
