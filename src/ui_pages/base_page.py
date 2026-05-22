"""Shared Playwright interaction primitives for all page objects."""

from __future__ import annotations

from typing import Final

import allure
from playwright.sync_api import Locator, Page, expect


class BasePage:
    """Base Page Object providing Allure-instrumented Playwright wrappers."""

    DEFAULT_TIMEOUT_MS: Final[int] = 10_000

    def __init__(self, page: Page) -> None:
        """Attach the active Playwright page instance.

        Args:
            page: Browser tab used to execute UI interactions.
        """
        self.page = page

    def click(
        self,
        locator: str,
        *,
        name: str | None = None,
        timeout_ms: int | None = None,
    ) -> None:
        """Click an element after recording the action in Allure."""
        step_name = name or f"Click '{locator}'"
        with allure.step(step_name):
            target = self._resolve_locator(locator, timeout_ms=timeout_ms)
            target.click()

    def fill(
        self,
        locator: str,
        value: str,
        *,
        name: str | None = None,
        timeout_ms: int | None = None,
    ) -> None:
        """Fill an input element after recording the action in Allure."""
        step_name = name or f"Fill '{locator}'"
        with allure.step(step_name):
            target = self._resolve_locator(locator, timeout_ms=timeout_ms)
            target.fill(value)

    def navigate(
        self,
        url: str,
        *,
        name: str | None = None,
        timeout_ms: int | None = None,
    ) -> None:
        """Navigate to a URL after recording the action in Allure."""
        step_name = name or f"Navigate to '{url}'"
        with allure.step(step_name):
            self.page.goto(url, timeout=timeout_ms or self.DEFAULT_TIMEOUT_MS)

    def wait_for_visible(
        self,
        locator: str,
        *,
        name: str | None = None,
        timeout_ms: int | None = None,
    ) -> Locator:
        """Wait until an element becomes visible and return its locator."""
        step_name = name or f"Wait for visible '{locator}'"
        with allure.step(step_name):
            target = self._resolve_locator(locator, timeout_ms=timeout_ms)
            expect(target).to_be_visible(timeout=timeout_ms or self.DEFAULT_TIMEOUT_MS)
            return target

    def _resolve_locator(self, locator: str, *, timeout_ms: int | None = None) -> Locator:
        """Resolve a selector string to a Playwright locator."""
        return self.page.locator(locator).first
