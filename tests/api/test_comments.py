"""Tests for Conduit article comment API endpoints."""

from __future__ import annotations

import allure
import pytest

from api_client.services.comments_service import CommentsService
from data_factory.builders import CommentDTO


@pytest.mark.regression
@allure.feature("Comments")
@allure.story("Comment creation")
@allure.title("POST /articles/{slug}/comments creates a comment")
def test_create_comment_on_article(
    comments_service: CommentsService,
    authenticated_token: str,
    created_article_slug: str,
) -> None:
    """Verify an authenticated user can comment on an existing article."""
    comment = CommentDTO.generate()

    with allure.step("Submit comment for existing article"):
        created = comments_service.create_comment(
            authenticated_token,
            created_article_slug,
            comment,
        )

    with allure.step("Verify comment was created successfully"):
        assert created.comment.body == comment.body
        assert created.comment.id > 0


@pytest.mark.regression
@allure.feature("Comments")
@allure.story("Comment listing")
@allure.title("GET /articles/{slug}/comments returns article comments")
def test_get_comments_for_article(
    comments_service: CommentsService,
    authenticated_token: str,
    created_article_slug: str,
) -> None:
    """Verify comments attached to an article can be retrieved as a collection."""
    comment = CommentDTO.generate()

    with allure.step("Create comment to populate comments collection"):
        comments_service.create_comment(authenticated_token, created_article_slug, comment)

    with allure.step("Request comments collection for article"):
        comments = comments_service.list_comments(created_article_slug)

    with allure.step("Verify comments collection contains created comment"):
        assert any(item.body == comment.body for item in comments.comments)


@pytest.mark.regression
@allure.feature("Comments")
@allure.story("Comment deletion")
@allure.title("DELETE /articles/{slug}/comments/{id} removes a comment")
def test_delete_comment_from_article(
    comments_service: CommentsService,
    authenticated_token: str,
    created_article_slug: str,
) -> None:
    """Verify the comment author can delete their comment from an article."""
    comment = CommentDTO.generate()

    with allure.step("Create comment to obtain comment identifier"):
        created = comments_service.create_comment(
            authenticated_token,
            created_article_slug,
            comment,
        )
        comment_id = created.comment.id

    with allure.step("Delete comment by identifier"):
        comments_service.delete_comment(authenticated_token, created_article_slug, comment_id)

    with allure.step("Verify deleted comment is absent from collection"):
        comments = comments_service.list_comments(created_article_slug)
        assert all(item.id != comment_id for item in comments.comments)
