"""Environment-driven configuration for the Conduit test automation framework."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Central configuration loaded from environment variables or a `.env` file.

    Attributes:
        BASE_URL: Root URL for Conduit API requests.
        UI_BASE_URL: Root URL for the Conduit frontend application.
        API_TIMEOUT: Default HTTP timeout in seconds for API calls.
        GEMINI_API_KEY: Optional API key reserved for future AI RCA integrations.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BASE_URL: str = Field(
        default="http://localhost:8000/api",
        description="Base URL for the Conduit API.",
    )
    UI_BASE_URL: str = Field(
        default="http://localhost:4200",
        description="Base URL for the Conduit frontend application.",
    )
    API_TIMEOUT: float = Field(
        default=10.0,
        gt=0,
        description="Default timeout in seconds for HTTP requests.",
    )
    GEMINI_API_KEY: str | None = Field(
        default=None,
        description="Optional Gemini API key for AI-assisted root cause analysis.",
    )
    ALLOW_SECURITY_FAILURES: bool = Field(
        default=False,
        description="When true, non-zero OWASP ZAP exit codes do not fail CI scripts.",
    )
    ALLOW_LOAD_FAILURES: bool = Field(
        default=False,
        description="When true, Locust threshold violations do not fail CI scripts.",
    )
    LOCUST_P95_THRESHOLD_MS: float = Field(
        default=2000.0,
        gt=0,
        description="Maximum allowed aggregated p95 response time in milliseconds.",
    )
    SECURITY_MAX_HIGH_ALERTS: int = Field(
        default=0,
        ge=0,
        description="Maximum allowed Medium+ OWASP ZAP alerts before CI fails.",
    )
