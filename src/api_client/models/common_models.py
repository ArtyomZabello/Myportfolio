"""Shared Pydantic models reused across Conduit API responses."""

from pydantic import BaseModel, Field


class AuthorProfile(BaseModel):
    """Embedded author/profile payload returned by RealWorld API resources."""

    username: str = Field(description="Public username of the author.")
    bio: str | None = Field(default=None, description="Optional author biography.")
    image: str | None = Field(default=None, description="Optional avatar URL.")
    following: bool = Field(default=False, description="Whether the viewer follows this profile.")
