"""Service layer for Conduit comment API operations."""

from __future__ import annotations

import allure

from api_client.base_client import BaseAPIClient
from api_client.exceptions import APIResponseError
from api_client.headers import authorization_headers
from api_client.models.comments_models import CommentResponse, CommentsListResponse
from config.constants import HTTP_OK, article_comment_path, article_comments_path
from data_factory.builders import CommentDTO


class CommentsService(BaseAPIClient):
    """Encapsulates article comment endpoints with typed responses."""

    def create_comment(self, token: str, slug: str, comment: CommentDTO) -> CommentResponse:
        """Add a comment to an article as an authenticated user."""
        endpoint = article_comments_path(slug)
        with allure.step(f"Create comment on article '{slug}'"):
            response = self._request(
                "POST",
                endpoint,
                json=comment.to_create_payload(),
                headers=authorization_headers(token),
            )
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="POST",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return CommentResponse.model_validate(response.json())

    def list_comments(self, slug: str) -> CommentsListResponse:
        """Retrieve all comments attached to an article."""
        endpoint = article_comments_path(slug)
        with allure.step(f"List comments for article '{slug}'"):
            response = self._request("GET", endpoint)
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="GET",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return CommentsListResponse.model_validate(response.json())

    def delete_comment(self, token: str, slug: str, comment_id: int) -> None:
        """Delete a comment authored by the authenticated user."""
        endpoint = article_comment_path(slug, comment_id)
        with allure.step(f"Delete comment {comment_id} from article '{slug}'"):
            response = self._request("DELETE", endpoint, headers=authorization_headers(token))
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="DELETE",
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_text=response.text,
                )
