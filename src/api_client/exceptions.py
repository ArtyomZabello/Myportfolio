"""Custom exceptions for the Conduit API client layer."""


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
    """

    def __init__(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_text: str,
    ) -> None:
        self.method = method
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"{method.upper()} {endpoint} returned {status_code}: {response_text}",
        )
