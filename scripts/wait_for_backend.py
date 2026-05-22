"""Poll the Conduit backend until the tags endpoint responds with HTTP 200."""

from __future__ import annotations

import sys
import time

import httpx

from config.settings import Config


def wait_for_backend(*, timeout_seconds: int = 30, poll_interval_seconds: float = 1.0) -> int:
    """Block until the backend health endpoint is reachable.

    Returns:
        ``0`` when the backend is ready, ``1`` on timeout.
    """
    config = Config()
    health_url = f"{config.BASE_URL.rstrip('/')}/tags"
    deadline = time.monotonic() + timeout_seconds

    print(f"Waiting for backend at {health_url} (timeout={timeout_seconds}s)...")

    while time.monotonic() < deadline:
        try:
            response = httpx.get(health_url, timeout=config.API_TIMEOUT)
            if response.status_code == 200:
                print(f"Backend is ready at {health_url}")
                return 0
        except httpx.HTTPError:
            pass

        time.sleep(poll_interval_seconds)

    print(f"Backend did not become healthy within {timeout_seconds} seconds.")
    return 1


if __name__ == "__main__":
    sys.exit(wait_for_backend())
