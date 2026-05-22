"""Locust load tests for the Conduit (RealWorld) API."""

from __future__ import annotations

import logging
import random
from typing import Final

from locust import FastHttpUser, between, task

from config.settings import Config

logger = logging.getLogger(__name__)

_CONFIG: Final[Config] = Config()
_API_HOST: Final[str] = _CONFIG.BASE_URL.rstrip("/")
_PROFILE_USERNAMES: Final[tuple[str, ...]] = ("jake", "john", "alice", "bob")


class UserBehavior(FastHttpUser):
    """Simulates a realistic read-heavy Conduit user journey.

    ``host`` is derived from ``Config.BASE_URL`` (for example,
    ``http://localhost:8000/api``), so task paths are relative API routes
    such as ``/tags`` rather than ``/api/tags``.

    Task weights reflect typical browsing patterns: users mostly read article
    feeds, occasionally browse tags or author profiles, and rarely attempt login.
    """

    host = _API_HOST
    wait_time = between(1, 3)

    def on_start(self) -> None:
        """Prepare the simulated user session before tasks execute."""
        logger.debug("Starting user session against host=%s", self.host)

    @task(5)
    def fetch_articles(self) -> None:
        """Fetch a paginated article feed (weight: 5)."""
        with self.client.get(
            "/articles?limit=10&offset=0",
            name="GET /articles",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                logger.warning("GET /articles returned status %s", response.status_code)

    @task(2)
    def fetch_tags(self) -> None:
        """Fetch all system tags (weight: 2)."""
        with self.client.get("/tags", name="GET /tags", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                logger.warning("GET /tags returned status %s", response.status_code)

    @task(1)
    def view_author_profile(self) -> None:
        """View a random author profile (weight: 1)."""
        username = random.choice(_PROFILE_USERNAMES)
        with self.client.get(
            f"/profiles/{username}",
            name="GET /profiles/{username}",
            catch_response=True,
        ) as response:
            if response.status_code not in (200, 404):
                response.failure(f"Expected 200 or 404, got {response.status_code}")
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
            "/users/login",
            json=payload,
            name="POST /users/login",
            catch_response=True,
        ) as response:
            if response.status_code in (401, 422):
                response.success()
            elif response.status_code != 200:
                response.failure(f"Unexpected status {response.status_code}")
                logger.warning("POST /users/login returned status %s", response.status_code)
