"""Service layer for Conduit authentication API operations."""

from __future__ import annotations

import allure

from api_client.base_client import BaseAPIClient
from api_client.exceptions import APIResponseError
from api_client.models.auth_models import UserResponse
from config.constants import API_PATH_USERS, API_PATH_USERS_LOGIN, HTTP_CREATED, HTTP_OK
from data_factory.builders import UserDTO


class AuthService(BaseAPIClient):
    """Encapsulates user registration and login with typed responses."""

    def register(self, user: UserDTO) -> UserResponse:
        """Register a new user and return the typed registration payload."""
        with allure.step("Register new user"):
            response = self._request("POST", API_PATH_USERS, json=user.to_registration_payload())
            if response.status_code != HTTP_CREATED:
                raise APIResponseError(
                    method="POST",
                    endpoint=API_PATH_USERS,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return UserResponse.model_validate(response.json())

    def login(self, *, email: str, password: str) -> UserResponse:
        """Authenticate an existing user and return the typed login payload."""
        with allure.step("Login with user credentials"):
            response = self._request(
                "POST",
                API_PATH_USERS_LOGIN,
                json={"user": {"email": email, "password": password}},
            )
            if response.status_code != HTTP_OK:
                raise APIResponseError(
                    method="POST",
                    endpoint=API_PATH_USERS_LOGIN,
                    status_code=response.status_code,
                    response_text=response.text,
                )
            return UserResponse.model_validate(response.json())

    def login_raw(self, credentials: dict[str, str]) -> int:
        """Return the HTTP status code for a raw login attempt."""
        response = self._request(
            "POST",
            API_PATH_USERS_LOGIN,
            json={"user": credentials},
        )
        return response.status_code

    def register_raw(self, payload: dict[str, dict[str, str]]) -> int:
        """Return the HTTP status code for a raw registration attempt."""
        response = self._request("POST", API_PATH_USERS, json=payload)
        return response.status_code
