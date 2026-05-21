"""Locust load tests for the Conduit (RealWorld) API."""

from __future__ import annotations

import logging
from typing import Final

from locust import FastHttpUser, between, task

from config.settings import Config

logger = logging.getLogger(__name__)

_CONFIG: Final[Config] = Config()
_API_HOST: Final[str] = _CONFIG.BASE_URL.rstrip("/")


class UserBehavior(FastHttpUser):
    """Simulates realistic read-heavy traffic against public Conduit endpoints.

    ``host`` is derived from ``Config.BASE_URL`` (for example,
    ``http://localhost:8000/api``), so task paths are relative API routes
    such as ``/tags`` rather than ``/api/tags``.
    """

    host = _API_HOST
    wait_time = between(1, 3)

    def on_start(self) -> None:
        """Prepare the simulated user session before tasks execute.

        Authentication would be performed here for protected routes (for example,
        POST ``/users/login`` followed by storing the JWT). Public read endpoints
        used in this profile do not require credentials.
        """
        logger.debug("Starting user session against host=%s", self.host)

    @task(3)
    def fetch_tags(self) -> None:
        """Fetch all system tags (weight: 3)."""
        with self.client.get("/tags", name="GET /tags", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                logger.warning("GET /tags returned status %s", response.status_code)

    @task(1)
    def fetch_articles(self) -> None:
        """Fetch a paginated article feed (weight: 1)."""
        with self.client.get(
            "/articles?limit=10&offset=0",
            name="GET /articles",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                logger.warning("GET /articles returned status %s", response.status_code)
