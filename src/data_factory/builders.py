"""Pydantic models and builders for generating realistic Conduit test data."""

from __future__ import annotations

from typing import ClassVar, Self

from faker import Faker
from pydantic import BaseModel, Field

from config.constants import (
    MOCK_UI_INVALID_EMAIL,
    MOCK_UI_INVALID_PASSWORD,
    MOCK_UI_INVALID_USERNAME,
    MOCK_UI_VALID_EMAIL,
    MOCK_UI_VALID_PASSWORD,
    MOCK_UI_VALID_USERNAME,
)


class UserDTO(BaseModel):
    """Synthetic user credentials for registration and authentication flows."""

    username: str = Field(description="Unique username for the Conduit application.")
    email: str = Field(description="Email address associated with the user.")
    password: str = Field(description="Plain-text password for UI or API login.")

    _faker: ClassVar[Faker] = Faker()

    @classmethod
    def generate(cls) -> Self:
        """Build a user populated with realistic fake credentials."""
        username = cls._faker.user_name()
        return cls(
            username=username,
            email=cls._faker.email(),
            password=cls._faker.password(length=12, special_chars=True, digits=True),
        )

    @classmethod
    def mock_ui_valid(cls) -> Self:
        """Return credentials accepted by the mock Conduit UI login fixture."""
        return cls(
            username=MOCK_UI_VALID_USERNAME,
            email=MOCK_UI_VALID_EMAIL,
            password=MOCK_UI_VALID_PASSWORD,
        )

    @classmethod
    def mock_ui_invalid(cls) -> Self:
        """Return credentials rejected by the mock Conduit UI login fixture."""
        return cls(
            username=MOCK_UI_INVALID_USERNAME,
            email=MOCK_UI_INVALID_EMAIL,
            password=MOCK_UI_INVALID_PASSWORD,
        )

    def to_registration_payload(self) -> dict[str, dict[str, str]]:
        """Return the RealWorld API registration request body."""
        return {"user": self.model_dump()}


class ArticleDTO(BaseModel):
    """Synthetic article payload for create and publish scenarios."""

    title: str = Field(description="Article headline.")
    description: str = Field(description="Short summary displayed in article lists.")
    body: str = Field(description="Full article content body.")
    tags: list[str] = Field(description="Topic tags attached to the article.")

    _faker: ClassVar[Faker] = Faker()

    @classmethod
    def generate(cls, *, tag_count: int = 3) -> Self:
        """Build an article populated with realistic fake content."""
        return cls(
            title=cls._faker.sentence(nb_words=4).rstrip("."),
            description=cls._faker.sentence(nb_words=8),
            body=cls._faker.paragraph(nb_sentences=5),
            tags=[cls._faker.word() for _ in range(tag_count)],
        )

    def to_create_request(self) -> dict[str, str | list[str]]:
        """Return the RealWorld API ``article`` object for create requests."""
        return {
            "title": self.title,
            "description": self.description,
            "body": self.body,
            "tagList": self.tags,
        }

    def to_create_payload(self) -> dict[str, dict[str, str | list[str]]]:
        """Return the full RealWorld API create-article request body."""
        return {"article": self.to_create_request()}

    def to_update_payload(self) -> dict[str, dict[str, str | list[str]]]:
        """Return the full RealWorld API update-article request body."""
        return {"article": self.to_create_request()}


class CommentDTO(BaseModel):
    """Synthetic comment payload for article discussion scenarios."""

    body: str = Field(description="Comment text body.")

    _faker: ClassVar[Faker] = Faker()

    @classmethod
    def generate(cls) -> Self:
        """Build a comment populated with realistic fake content."""
        return cls(body=cls._faker.paragraph(nb_sentences=2))

    def to_create_payload(self) -> dict[str, dict[str, str]]:
        """Return the full RealWorld API create-comment request body."""
        return {"comment": {"body": self.body}}

