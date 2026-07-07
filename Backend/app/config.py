"""Application settings loaded from environment variables using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Sneaker Recommendation API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sneaker Recommendation API"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # comma-separated list of CORS origins
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Database Settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sneakers"

    # Pipeline/Search Provider settings
    search_provider: str = "duckduckgo"

    # Cloudinary (Phase 3 image enrichment)
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    # SerpAPI (alternative search provider)
    serpapi_key: str | None = None

    # ML Config (Phase 4+)
    model_path: str = "ml/artifacts/model.pkl"
    enable_st_rerank: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        """Split CORS origins from env string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
