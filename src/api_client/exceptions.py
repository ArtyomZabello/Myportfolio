"""Custom exceptions for the Conduit API client layer."""

from __future__ import annotations

import allure


class APIClientError(Exception):
    """Base exception for all API client failures."""


class APIRequestError(APIClientError):
    """Raised when an HTTP request cannot be completed due to transport errors.

    Attributes:
        method: HTTP verb used for the failed request.
        endpoint: Relative API path that was requested.
        message: Human-readable failure description.
    """

    def __init__(self, method: str, endpoint: str, message: str) -> None:
        self.method = method
        self.endpoint = endpoint
        self.message = message
        super().__init__(f"{method.upper()} {endpoint} failed: {message}")


class APIResponseError(APIClientError):
    """Raised when an HTTP response indicates a client or server error.

    Attributes:
        method: HTTP verb used for the request.
        endpoint: Relative API path that was requested.
        status_code: HTTP status code returned by the server.
        response_text: Raw response body for diagnostics.
        request_payload: Serialized request body when available.
    """

    def __init__(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_text: str,
        request_payload: str | None = None,
    ) -> None:
        self.method = method
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_text = response_text
        self.request_payload = request_payload
        self._attach_diagnostics()
        super().__init__(
            f"{method.upper()} {endpoint} returned {status_code}: {response_text}",
        )

    def _attach_diagnostics(self) -> None:
        """Attach API failure context to the active Allure report."""
        allure.attach(
            self.method,
            name="Failed Request Method",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            self.endpoint,
            name="Failed Request Endpoint",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            str(self.status_code),
            name="Failed Response Status",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            self.response_text,
            name="Failed Response Body",
            attachment_type=allure.attachment_type.TEXT,
        )
        if self.request_payload is not None:
            allure.attach(
                self.request_payload,
                name="Failed Request Payload",
                attachment_type=allure.attachment_type.TEXT,
            )
