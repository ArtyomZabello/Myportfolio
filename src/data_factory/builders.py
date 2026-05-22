"""Pydantic models and builders for generating realistic Conduit test data."""

from __future__ import annotations

from typing import ClassVar, Self

from faker import Faker
from pydantic import BaseModel, Field


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
