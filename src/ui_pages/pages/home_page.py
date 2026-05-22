"""Home page interactions for the Conduit RealWorld application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ui_pages.base_page import BasePage

if TYPE_CHECKING:
    from ui_pages.pages.login_page import LoginPage


class HomePage(BasePage):
    """Page Object for the Conduit landing page and global navigation."""

    SIGN_IN_LINK: Final[str] = "a[href='/login']"
    GLOBAL_FEED_TAB: Final[str] = "a[href='/']"

    def open_sign_in(self) -> LoginPage:
        """Navigate to the sign-in page using the top navigation link."""
        from ui_pages.pages.login_page import LoginPage

        self.click(self.SIGN_IN_LINK, name="Open sign-in page")
        return LoginPage(self.page)

    def assert_home_page_loaded(self) -> HomePage:
        """Assert that primary home page navigation elements are visible."""
        self.wait_for_visible(self.GLOBAL_FEED_TAB, name="Verify Global Feed tab is visible")
        self.wait_for_visible(self.SIGN_IN_LINK, name="Verify Sign in link is visible")
        return self
