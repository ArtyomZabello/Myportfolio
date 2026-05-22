"""Pydantic models for Conduit article API responses."""

from pydantic import BaseModel, Field

from api_client.models.common_models import AuthorProfile


class ArticleModel(BaseModel):
    """Single article resource returned by the RealWorld API."""

    slug: str = Field(description="URL-friendly article identifier.")
    title: str = Field(description="Article headline.")
    description: str = Field(description="Short summary shown in feeds.")
    body: str = Field(description="Full article content.")
    tagList: list[str] = Field(
        default_factory=list,
        description="Topic tags attached to the article.",
    )
    createdAt: str | None = Field(default=None, description="Creation timestamp.")
    updatedAt: str | None = Field(default=None, description="Last update timestamp.")
    favorited: bool = Field(default=False, description="Whether the viewer favorited the article.")
    favoritesCount: int = Field(default=0, description="Total favorites count.")
    author: AuthorProfile = Field(description="Author profile embedded in the article.")


class ArticleResponse(BaseModel):
    """Validated response payload for single-article endpoints."""

    article: ArticleModel


class ArticlesFeedResponse(BaseModel):
    """Validated response payload for paginated article feeds."""

    articles: list[ArticleModel] = Field(description="Articles returned for the requested page.")
    articlesCount: int = Field(description="Total number of articles in the feed.")
