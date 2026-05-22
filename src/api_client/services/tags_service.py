"""Service layer for Conduit tag-related API operations."""

import allure

from api_client.base_client import BaseAPIClient
from api_client.exceptions import APIResponseError
from api_client.models.tags_models import TagsResponse
from config.constants import API_PATH_TAGS, HTTP_OK


class TagsService(BaseAPIClient):
    """Encapsulates tag endpoints with typed request and response handling."""

    def get_tags(self) -> TagsResponse:
        """Retrieve all system tags from the Conduit API.

        Returns:
            Parsed and validated tags response.

        Raises:
            APIRequestError: If the HTTP request fails at the transport layer.
            APIResponseError: If the server returns a non-success status code.
            ValidationError: If the response body does not match ``TagsResponse``.
        """
        with allure.step("Retrieve system tags"):
            response = self._request("GET", API_PATH_TAGS)

            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="GET",
                    endpoint=API_PATH_TAGS,
                    status_code=response.status_code,
                    response_text=response.text,
                )

            return TagsResponse.model_validate(response.json())
