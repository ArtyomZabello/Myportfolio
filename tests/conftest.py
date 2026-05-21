"""Shared pytest fixtures for the Conduit test automation suite."""

from collections.abc import Generator

import pytest

from api_client.base_client import BaseAPIClient
from api_client.services.tags_service import TagsService
from config.settings import Config


@pytest.fixture(scope="session")
def config() -> Config:
    """Provide session-scoped application configuration."""
    return Config()


@pytest.fixture(scope="session")
def api_client(config: Config) -> Generator[BaseAPIClient, None, None]:
    """Provide a session-scoped API client bound to the resolved configuration."""
    client = BaseAPIClient(config)
    yield client
    client.close()


@pytest.fixture(scope="session")
def tags_service(config: Config) -> Generator[TagsService, None, None]:
    """Provide a session-scoped tags service bound to the resolved configuration."""
    service = TagsService(config)
    yield service
    service.close()
