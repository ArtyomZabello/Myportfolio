"""Synchronous HTTP client foundation for Conduit API interactions."""

import json
from typing import Any

import allure
import httpx

from api_client.exceptions import APIRequestError
from config.settings import Config


class BaseAPIClient:
    """Reusable synchronous HTTP client configured for the Conduit API.

    This class owns transport configuration and request execution. Callers
    receive raw ``httpx.Response`` objects and decide how to validate them.
    """

    def __init__(self, config: Config) -> None:
        """Initialize the client with environment-driven settings.

        Args:
            config: Resolved application configuration.
        """
        self._config = config
        self._client = httpx.Client(
            base_url=config.BASE_URL,
            timeout=config.API_TIMEOUT,
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute an HTTP request and record request/response metadata in Allure.

        Args:
            method: HTTP verb (for example, ``GET`` or ``POST``).
            endpoint: Relative API path appended to ``BASE_URL``.
            **kwargs: Additional arguments forwarded to ``httpx.Client.request``.

        Returns:
            The HTTP response returned by the server.

        Raises:
            APIRequestError: If the request fails before a response is received.
        """
        normalized_method = method.upper()
        step_title = f"{normalized_method} {endpoint}"

        with allure.step(step_title):
            allure.attach(
                self._config.BASE_URL,
                name="Base URL",
                attachment_type=allure.attachment_type.TEXT,
            )

            request_json = kwargs.get("json")
            if request_json is not None:
                allure.attach(
                    json.dumps(request_json, default=str),
                    name="Request JSON",
                    attachment_type=allure.attachment_type.JSON,
                )

            try:
                response = self._client.request(normalized_method, endpoint, **kwargs)
            except httpx.RequestError as exc:
                allure.attach(
                    str(exc),
                    name="Transport Error",
                    attachment_type=allure.attachment_type.TEXT,
                )
                raise APIRequestError(
                    method=normalized_method,
                    endpoint=endpoint,
                    message=str(exc),
                ) from exc

            allure.attach(
                str(response.status_code),
                name="Status Code",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.JSON
                if "application/json" in response.headers.get("content-type", "")
                else allure.attachment_type.TEXT,
            )

            return response

    def get(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Send a GET request to the given endpoint."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Send a POST request to the given endpoint."""
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Send a PUT request to the given endpoint."""
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Send a PATCH request to the given endpoint."""
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Send a DELETE request to the given endpoint."""
        return self._request("DELETE", endpoint, **kwargs)
