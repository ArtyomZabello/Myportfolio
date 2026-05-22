"""Authentication and navigation UI tests for the Conduit frontend."""

import allure
import pytest

from data_factory.builders import UserDTO
from ui_pages.app import App


@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("Authentication")
@allure.story("Navigation")
@allure.title("Navigate to sign-in page from home")
def test_user_can_navigate_to_login_page(ui_app: App) -> None:
    """Verify a user can reach the sign-in page and see the login form."""
    with allure.step("Verify home page is loaded"):
        ui_app.home_page.assert_home_page_loaded()

    with allure.step("Open sign-in page from navigation"):
        login_page = ui_app.home_page.open_sign_in()

    with allure.step("Verify sign-in form is visible"):
        login_page.assert_sign_in_form_visible()


@pytest.mark.regression
@allure.feature("Authentication")
@allure.story("Login form")
@allure.title("Enter generated credentials into sign-in form")
def test_login_form_accepts_generated_user_credentials(ui_app: App) -> None:
    """Verify generated user credentials can be entered into the sign-in form."""
    user = UserDTO.generate()

    with allure.step("Open sign-in page"):
        ui_app.home_page.open_sign_in()

    with allure.step("Enter generated credentials and verify form remains visible"):
        ui_app.login_page.fill_credentials(user).assert_sign_in_form_visible()
