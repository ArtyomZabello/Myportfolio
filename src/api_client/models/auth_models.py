"""Pydantic models for Conduit authentication API responses."""

from pydantic import BaseModel, Field


class UserModel(BaseModel):
    """Authenticated or registered user payload."""

    email: str = Field(description="User email address.")
    token: str = Field(description="Bearer token for subsequent authenticated requests.")
    username: str = Field(description="Unique username.")
    bio: str | None = Field(default=None, description="Optional user biography.")
    image: str | None = Field(default=None, description="Optional avatar URL.")


class UserResponse(BaseModel):
    """Validated response payload for user registration and login."""

    user: UserModel
