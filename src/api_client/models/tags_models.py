"""Pydantic models for the Conduit tags API."""

from pydantic import BaseModel, Field


class TagsResponse(BaseModel):
    """Validated response payload for ``GET /tags``.

    Example:
        {"tags": ["react", "angular", "node"]}
    """

    tags: list[str] = Field(
        description="List of tag names exposed by the Conduit API.",
    )
