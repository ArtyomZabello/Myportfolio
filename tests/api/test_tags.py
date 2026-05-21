"""Tests for Conduit tag-related API endpoints."""

from api_client.models.tags_models import TagsResponse
from api_client.services.tags_service import TagsService


def test_get_tags_returns_valid_response(tags_service: TagsService) -> None:
    """Verify the tags service returns a validated TagsResponse with a list payload."""
    response: TagsResponse = tags_service.get_tags()

    assert isinstance(response, TagsResponse)
    assert isinstance(response.tags, list)
