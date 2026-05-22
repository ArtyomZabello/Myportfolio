"""Application facade exposing lazy page object properties."""

from __future__ import annotations

from playwright.sync_api import Page

from ui_pages.pages.home_page import HomePage
from ui_pages.pages.login_page import LoginPage


class App:
    """Central entry point for interacting with the Conduit UI via Page Objects."""

    def __init__(self, page: Page) -> None:
        """Initialize the application facade.

        Args:
            page: Active Playwright page bound to the Conduit frontend.
        """
        self.page = page
        self._home_page: HomePage | None = None
        self._login_page: LoginPage | None = None

    @property
    def home_page(self) -> HomePage:
        """Return the home page object, creating it lazily on first access."""
        if self._home_page is None:
            self._home_page = HomePage(self.page)
        return self._home_page

    @property
    def login_page(self) -> LoginPage:
        """Return the login page object, creating it lazily on first access."""
        if self._login_page is None:
            self._login_page = LoginPage(self.page)
        return self._login_page
