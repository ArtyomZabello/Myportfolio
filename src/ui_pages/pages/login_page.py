"""Login page interactions for the Conduit RealWorld application."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from data_factory.builders import UserDTO
from ui_pages.base_page import BasePage

if TYPE_CHECKING:
    from ui_pages.pages.home_page import HomePage


class LoginPage(BasePage):
    """Page Object for the Conduit sign-in form."""

    EMAIL_INPUT: Final[str] = "input[placeholder='Email']"
    PASSWORD_INPUT: Final[str] = "input[placeholder='Password']"
    SIGN_IN_BUTTON: Final[str] = "button:has-text('Sign in')"

    def login(self, user: UserDTO) -> HomePage:
        """Fill credentials and submit the sign-in form.

        Args:
            user: Generated or predefined user credentials.

        Returns:
            Home page object reached after successful authentication.
        """
        with self.page.expect_navigation():
            self.fill(self.EMAIL_INPUT, user.email, name="Fill email address")
            self.fill(self.PASSWORD_INPUT, user.password, name="Fill password")
            self.click(self.SIGN_IN_BUTTON, name="Submit sign in form")
        from ui_pages.pages.home_page import HomePage

        return HomePage(self.page)

    def assert_sign_in_form_visible(self) -> LoginPage:
        """Assert that the sign-in form controls are visible."""
        self.wait_for_visible(self.EMAIL_INPUT, name="Assert email field is visible")
        self.wait_for_visible(self.PASSWORD_INPUT, name="Assert password field is visible")
        self.wait_for_visible(self.SIGN_IN_BUTTON, name="Assert sign in button is visible")
        return self

    def fill_credentials(self, user: UserDTO) -> LoginPage:
        """Populate the sign-in form with the provided user credentials."""
        self.fill(self.EMAIL_INPUT, user.email, name="Fill email address")
        self.fill(self.PASSWORD_INPUT, user.password, name="Fill password")
        return self
