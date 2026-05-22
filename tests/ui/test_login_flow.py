"""Login flow UI tests for the Conduit frontend."""

from __future__ import annotations

import allure
import pytest

from config.constants import MOCK_UI_LOGIN_ERROR_MESSAGE
from data_factory.builders import UserDTO
from ui_pages.app import App


@pytest.mark.smoke
@pytest.mark.regression
@allure.feature("Authentication")
@allure.story("Login flow")
@allure.title("Sign in with valid credentials")
def test_successful_login(ui_app: App) -> None:
    """Verify a user with valid credentials is redirected to the home page after sign-in."""
    valid_user = UserDTO.mock_ui_valid()

    with allure.step("Open sign-in page from home navigation"):
        ui_app.home_page.assert_home_page_loaded()
        ui_app.home_page.open_sign_in()
        ui_app.login_page.assert_sign_in_form_visible()

    with allure.step("Submit valid credentials and verify home page is loaded"):
        ui_app.login_page.login(valid_user)
        ui_app.home_page.assert_home_page_loaded()


@pytest.mark.regression
@allure.feature("Authentication")
@allure.story("Login flow")
@allure.title("Show error message for invalid credentials")
def test_failed_login_shows_error_message(ui_app: App) -> None:
    """Verify invalid credentials keep the user on the login page with an error message."""
    invalid_user = UserDTO.mock_ui_invalid()

    with allure.step("Open sign-in page from home navigation"):
        ui_app.home_page.assert_home_page_loaded()
        ui_app.home_page.open_sign_in()
        ui_app.login_page.assert_sign_in_form_visible()

    with allure.step("Submit invalid credentials"):
        ui_app.login_page.fill_credentials(invalid_user).submit_login()

    with allure.step("Verify login error message is displayed"):
        ui_app.login_page.assert_login_error_visible(message=MOCK_UI_LOGIN_ERROR_MESSAGE)
