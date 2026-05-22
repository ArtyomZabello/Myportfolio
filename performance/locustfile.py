"""Locust load tests for the Conduit (RealWorld) API."""

from __future__ import annotations

import logging
import random
from typing import Final

from locust import FastHttpUser, between, task

from config.constants import (
    API_PATH_ARTICLES,
    API_PATH_TAGS,
    API_PATH_USERS_LOGIN,
    HTTP_NOT_FOUND,
    HTTP_OK,
    LOCUST_ARTICLE_PAGE_LIMIT,
    LOCUST_ARTICLE_PAGE_OFFSET,
    LOCUST_PROFILE_USERNAMES,
    LOCUST_WAIT_MAX_SECONDS,
    LOCUST_WAIT_MIN_SECONDS,
    REJECTED_AUTH_STATUSES,
    REJECTED_VALIDATION_STATUSES,
    profile_path,
)
from config.settings import Config

logger = logging.getLogger(__name__)

_CONFIG: Final[Config] = Config()
_API_HOST: Final[str] = _CONFIG.BASE_URL.rstrip("/")
_ARTICLES_QUERY: Final[str] = (
    f"{API_PATH_ARTICLES}?limit={LOCUST_ARTICLE_PAGE_LIMIT}&offset={LOCUST_ARTICLE_PAGE_OFFSET}"
)


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
        """View a random author profile (weight: 1)."""
        username = random.choice(LOCUST_PROFILE_USERNAMES)
        endpoint = profile_path(username)
        with self.client.get(
            endpoint,
            name="GET /profiles/{username}",
            catch_response=True,
        ) as response:
            if response.status_code not in (HTTP_OK, HTTP_NOT_FOUND):
                response.failure(
                    f"Expected {HTTP_OK} or {HTTP_NOT_FOUND}, got {response.status_code}",
                )
                logger.warning(
                    "GET /profiles/%s returned status %s",
                    username,
                    response.status_code,
                )

    @task(1)
    def attempt_login(self) -> None:
        """Attempt login with fake credentials to stress password hashing (weight: 1)."""
        payload = {
            "user": {
                "email": f"loadtest_{random.randint(1, 100_000)}@example.com",
                "password": f"WrongPassword{random.randint(1, 100_000)}!",
            }
        }
        with self.client.post(
            API_PATH_USERS_LOGIN,
            json=payload,
            name="POST /users/login",
            catch_response=True,
        ) as response:
            if response.status_code in REJECTED_AUTH_STATUSES | REJECTED_VALIDATION_STATUSES:
                response.success()
            elif response.status_code != HTTP_OK:
                response.failure(f"Unexpected status {response.status_code}")
                logger.warning("POST /users/login returned status %s", response.status_code)
