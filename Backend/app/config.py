"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API skeleton."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Sneaker Recommendation API"
    app_version: str = "0.1.0"
    debug: bool = True

    # comma-separated list in .env, e.g. http://localhost:5173,http://localhost:3000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = "postgresql://postgres:postgres@localhost:5432/sneakers"

    @property
    def cors_origin_list(self) -> list[str]:
        """Split CORS origins from env string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
