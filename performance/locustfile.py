"""Locust load tests for the Conduit (RealWorld) API."""

from __future__ import annotations

import logging
import random
from pathlib import Path
from typing import Final

from locust import FastHttpUser, between, task

from config.constants import (
    API_PATH_ARTICLES,
    API_PATH_TAGS,
    API_PATH_USERS_LOGIN,
    HTTP_OK,
    LOCUST_ARTICLE_PAGE_LIMIT,
    LOCUST_ARTICLE_PAGE_OFFSET,
    LOCUST_DATASET_V1_PATH,
    LOCUST_WAIT_MAX_SECONDS,
    LOCUST_WAIT_MIN_SECONDS,
    LOGIN_REJECTION_STATUSES,
    PROFILE_LOOKUP_BACKEND_ANOMALY_STATUSES,
    PROFILE_LOOKUP_MISSING_STATUSES,
    PROFILE_LOOKUP_SUCCESS_STATUSES,
    profile_path,
)
from config.settings import Config
from performance.seed_load_data import load_dataset

logger = logging.getLogger(__name__)

_CONFIG: Final[Config] = Config()
_API_HOST: Final[str] = _CONFIG.BASE_URL.rstrip("/")
_ARTICLES_QUERY: Final[str] = (
    f"{API_PATH_ARTICLES}?limit={LOCUST_ARTICLE_PAGE_LIMIT}&offset={LOCUST_ARTICLE_PAGE_OFFSET}"
)
_DATASET_PATH: Final[Path] = Path(__file__).resolve().parents[1] / LOCUST_DATASET_V1_PATH


def _read_load_data() -> tuple[list[str], list[str]]:
    """Load profile usernames and login rejection emails from the v1 dataset."""
    payload = load_dataset(_DATASET_PATH)
    profile_usernames = [user["username"] for user in payload["profile_users"]]
    login_rejection_emails = payload["login_rejection_emails"]
    return profile_usernames, login_rejection_emails


def _profile_response_failure_reason(
    *,
    status_code: int,
    username: str,
    response_text: str,
) -> str | None:
    """Classify profile lookup responses; return a failure reason or None on success."""
    if status_code in PROFILE_LOOKUP_SUCCESS_STATUSES:
        return None

    if status_code in PROFILE_LOOKUP_MISSING_STATUSES:
        return (
            f"Seeded profile '{username}' returned 404 — dataset/backend mismatch "
            f"(expected 200 after verify step)."
        )

    if status_code in PROFILE_LOOKUP_BACKEND_ANOMALY_STATUSES:
        logger.warning(
            "Backend anomaly for seeded profile '%s': status=%s body=%s",
            username,
            status_code,
            response_text,
        )
        return (
            f"Backend anomaly ({status_code}) for seeded profile '{username}' — "
            "FastAPI SUT may return 400 instead of RealWorld 404 for missing users."
        )

    return f"Unexpected profile status {status_code} for seeded user '{username}'"


_PROFILE_USERNAMES, _LOGIN_REJECTION_EMAILS = _read_load_data()


class UserBehavior(FastHttpUser):
    """Simulates a realistic read-heavy Conduit user journey.

    ``host`` is derived from ``Config.BASE_URL`` (for example,
    ``http://localhost:8000/api``), so task paths are relative API routes
    such as ``/tags`` rather than ``/api/tags``.

    Task weights reflect typical browsing patterns: users mostly read article
    feeds, occasionally browse tags or author profiles, and rarely attempt login.
    """

    host = _API_HOST
    wait_time = between(LOCUST_WAIT_MIN_SECONDS, LOCUST_WAIT_MAX_SECONDS)

    def on_start(self) -> None:
        """Prepare the simulated user session before tasks execute."""
        logger.debug("Starting user session against host=%s", self.host)

    @task(5)
    def fetch_articles(self) -> None:
        """Fetch a paginated article feed (weight: 5)."""
        with self.client.get(
            _ARTICLES_QUERY,
            name="GET /articles",
            catch_response=True,
        ) as response:
            if response.status_code != HTTP_OK:
                response.failure(f"Expected {HTTP_OK}, got {response.status_code}")
                logger.warning("GET /articles returned status %s", response.status_code)

    @task(2)
    def fetch_tags(self) -> None:
        """Fetch all system tags (weight: 2)."""
        with self.client.get(
            API_PATH_TAGS,
            name="GET /tags",
            catch_response=True,
        ) as response:
            if response.status_code != HTTP_OK:
                response.failure(f"Expected {HTTP_OK}, got {response.status_code}")
                logger.warning("GET /tags returned status %s", response.status_code)

    @task(1)
    def view_author_profile(self) -> None:
        """View a seeded author profile (weight: 1)."""
        username = random.choice(_PROFILE_USERNAMES)
        endpoint = profile_path(username)
        with self.client.get(
            endpoint,
            name="GET /profiles/{username}",
            catch_response=True,
        ) as response:
            failure_reason = _profile_response_failure_reason(
                status_code=response.status_code,
                username=username,
                response_text=response.text,
            )
            if failure_reason is not None:
                response.failure(failure_reason)

    @task(1)
    def attempt_login(self) -> None:
        """Attempt login with seeded non-existent credentials (weight: 1)."""
        email = random.choice(_LOGIN_REJECTION_EMAILS)
        payload = {
            "user": {
                "email": email,
                "password": "WrongPasswordForLoadTest!",
            }
        }
        with self.client.post(
            API_PATH_USERS_LOGIN,
            json=payload,
            name="POST /users/login",
            catch_response=True,
        ) as response:
            if response.status_code in LOGIN_REJECTION_STATUSES:
                response.success()
            elif response.status_code != HTTP_OK:
                response.failure(f"Unexpected status {response.status_code}")
                logger.warning("POST /users/login returned status %s", response.status_code)
