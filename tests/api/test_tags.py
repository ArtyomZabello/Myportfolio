"""Tests for Conduit tag-related API endpoints."""

import allure
import pytest

from api_client.models.tags_models import TagsResponse
from api_client.services.tags_service import TagsService


@pytest.mark.smoke
@pytest.mark.contract
@allure.feature("Tags")
@allure.story("Tag listing")
@allure.title("GET /tags returns a validated tag list")
def test_get_tags_returns_valid_response(tags_service: TagsService) -> None:
    """Verify the tags service returns a validated TagsResponse with a list payload."""
    with allure.step("Retrieve system tags via service layer"):
        response: TagsResponse = tags_service.get_tags()

    with allure.step("Verify response model and tag collection type"):
        assert isinstance(response, TagsResponse)
        assert isinstance(response.tags, list)
