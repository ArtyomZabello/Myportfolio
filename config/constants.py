"""Shared constants for the Conduit test automation framework."""

from typing import Final

# ---------------------------------------------------------------------------
# API endpoint paths (relative to ``Config.BASE_URL``)
# ---------------------------------------------------------------------------
API_PATH_TAGS: Final[str] = "/tags"
API_PATH_ARTICLES: Final[str] = "/articles"
API_PATH_USERS: Final[str] = "/users"
API_PATH_USERS_LOGIN: Final[str] = "/users/login"


def profile_path(username: str) -> str:
    """Build the relative profile endpoint for the given username."""
    return f"/profiles/{username}"


def article_path(slug: str) -> str:
    """Build the relative single-article endpoint."""
    return f"/articles/{slug}"


def article_comments_path(slug: str) -> str:
    """Build the relative article comments collection endpoint."""
    return f"/articles/{slug}/comments"


def article_comment_path(slug: str, comment_id: int) -> str:
    """Build the relative single-comment endpoint."""
    return f"/articles/{slug}/comments/{comment_id}"


# ---------------------------------------------------------------------------
# HTTP status codes referenced across API and load tests
# ---------------------------------------------------------------------------
HTTP_OK: Final[int] = 200
HTTP_CREATED: Final[int] = 201
HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_UNPROCESSABLE: Final[int] = 422
HTTP_NOT_FOUND: Final[int] = 404
HTTP_FORBIDDEN: Final[int] = 403

# ---------------------------------------------------------------------------
# Backend health polling (``scripts/wait_for_backend.py``)
# ---------------------------------------------------------------------------
BACKEND_HEALTH_TIMEOUT_SECONDS: Final[int] = 30
BACKEND_POLL_INTERVAL_SECONDS: Final[float] = 1.0

# ---------------------------------------------------------------------------
# Locust load profile
# ---------------------------------------------------------------------------
LOCUST_ARTICLE_PAGE_LIMIT: Final[int] = 10
LOCUST_ARTICLE_PAGE_OFFSET: Final[int] = 0
LOCUST_PROFILE_USERNAMES: Final[tuple[str, ...]] = ("jake", "john", "alice", "bob")
LOCUST_WAIT_MIN_SECONDS: Final[float] = 1.0
LOCUST_WAIT_MAX_SECONDS: Final[float] = 3.0

# ---------------------------------------------------------------------------
# Mock UI credentials (must stay in sync with ``scripts/mock_conduit_ui/login.html``)
# ---------------------------------------------------------------------------
MOCK_UI_VALID_USERNAME: Final[str] = "testuser"
MOCK_UI_VALID_EMAIL: Final[str] = "test@example.com"
MOCK_UI_VALID_PASSWORD: Final[str] = "password123"
MOCK_UI_INVALID_USERNAME: Final[str] = "baduser"
MOCK_UI_INVALID_EMAIL: Final[str] = "wrong@example.com"
MOCK_UI_INVALID_PASSWORD: Final[str] = "wrongpassword"
MOCK_UI_LOGIN_ERROR_MESSAGE: Final[str] = "Invalid email or password"

# ---------------------------------------------------------------------------
# AI RCA demonstration payload
# ---------------------------------------------------------------------------
DEMO_INVALID_REGISTRATION_EMAIL: Final[str] = "plainaddress"
