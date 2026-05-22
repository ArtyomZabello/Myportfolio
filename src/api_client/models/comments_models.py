"""Pydantic models for Conduit comment API responses."""

from pydantic import BaseModel, Field

from api_client.models.common_models import AuthorProfile


class CommentModel(BaseModel):
    """Single comment resource returned by the RealWorld API."""

    id: int = Field(description="Unique comment identifier.")
    body: str = Field(description="Comment text body.")
    createdAt: str | None = Field(default=None, description="Creation timestamp.")
    updatedAt: str | None = Field(default=None, description="Last update timestamp.")
    author: AuthorProfile = Field(description="Author profile embedded in the comment.")


class CommentResponse(BaseModel):
    """Validated response payload for comment creation."""

    comment: CommentModel


class CommentsListResponse(BaseModel):
    """Validated response payload for article comment collections."""

    comments: list[CommentModel] = Field(description="Comments attached to an article.")
