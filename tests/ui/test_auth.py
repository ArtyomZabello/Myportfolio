"""Authentication and navigation UI tests for the Conduit frontend."""

import allure

from data_factory.builders import UserDTO
from ui_pages.app import App


@allure.feature("Authentication")
@allure.story("Navigation")
def test_user_can_navigate_to_login_page(ui_app: App) -> None:
    """Verify a user can reach the sign-in page and see the login form."""
    ui_app.home_page.assert_home_page_loaded()

    login_page = ui_app.home_page.open_sign_in()
    login_page.assert_sign_in_form_visible()


@allure.feature("Authentication")
@allure.story("Login form")
def test_login_form_accepts_generated_user_credentials(ui_app: App) -> None:
    """Verify generated user credentials can be entered into the sign-in form."""
    user = UserDTO.generate()

    ui_app.home_page.open_sign_in()
    ui_app.login_page.fill_credentials(user).assert_sign_in_form_visible()
