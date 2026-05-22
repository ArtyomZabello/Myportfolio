"""Poll the Conduit frontend until the mock or real UI responds."""

from __future__ import annotations

import sys
import time

import httpx

from config.constants import BACKEND_HEALTH_TIMEOUT_SECONDS, BACKEND_POLL_INTERVAL_SECONDS
from config.settings import Config


def wait_for_ui(
    *,
    timeout_seconds: int = BACKEND_HEALTH_TIMEOUT_SECONDS,
    poll_interval_seconds: float = BACKEND_POLL_INTERVAL_SECONDS,
) -> int:
    """Block until the frontend root URL responds successfully.

    Returns:
        ``0`` when the UI is ready, ``1`` on timeout.
    """
    config = Config()
    ui_url = config.UI_BASE_URL.rstrip("/")
    deadline = time.monotonic() + timeout_seconds

    print(f"Waiting for UI at {ui_url} (timeout={timeout_seconds}s)...")

    while time.monotonic() < deadline:
        try:
            response = httpx.get(ui_url, timeout=config.API_TIMEOUT, follow_redirects=True)
            if response.status_code == 200:
                print(f"UI is ready at {ui_url}")
                return 0
        except httpx.HTTPError:
            pass

        time.sleep(poll_interval_seconds)

    print(f"UI did not become healthy within {timeout_seconds} seconds.")
    return 1


if __name__ == "__main__":
    sys.exit(wait_for_ui())
