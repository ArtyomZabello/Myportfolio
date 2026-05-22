"""Login flow UI tests for the Conduit frontend."""

from __future__ import annotations

import allure

from data_factory.builders import UserDTO
from ui_pages.app import App

_VALID_LOGIN_USER = UserDTO(
    username="testuser",
    email="test@example.com",
    password="password123",
)
_INVALID_LOGIN_USER = UserDTO(
    username="baduser",
    email="wrong@example.com",
    password="wrongpassword",
)


@allure.feature("Authentication")
@allure.story("Login flow")
@allure.title("User can sign in with valid credentials")
def test_successful_login(ui_app: App) -> None:
    """Verify a user with valid credentials is redirected to the home page after sign-in."""
    with allure.step("Open the sign-in page from the home navigation"):
        ui_app.home_page.assert_home_page_loaded()
        ui_app.home_page.open_sign_in()
        ui_app.login_page.assert_sign_in_form_visible()

    with allure.step("Submit valid credentials and land on the home page"):
        ui_app.login_page.login(_VALID_LOGIN_USER)
        ui_app.home_page.assert_home_page_loaded()


@allure.feature("Authentication")
@allure.story("Login flow")
@allure.title("Invalid credentials show an error message on the sign-in form")
def test_failed_login_shows_error_message(ui_app: App) -> None:
    """Verify invalid credentials keep the user on the login page with an error message."""
    with allure.step("Open the sign-in page from the home navigation"):
        ui_app.home_page.assert_home_page_loaded()
        ui_app.home_page.open_sign_in()
        ui_app.login_page.assert_sign_in_form_visible()

    with allure.step("Submit invalid credentials"):
        ui_app.login_page.fill_credentials(_INVALID_LOGIN_USER).submit_login()

    with allure.step("Verify an error message is displayed on the page"):
        ui_app.login_page.assert_login_error_visible(message="Invalid email or password")
