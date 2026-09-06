"""Application configuration.

Settings are loaded from environment variables (or a local .env file).
Keeping this isolated means swapping SQLite for PostgreSQL later is just
a matter of changing DATABASE_URL - no code changes required.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Defaults to a local SQLite file for easy local development.
    # Swap for a PostgreSQL URL (postgresql+psycopg://...) in production.
    database_url: str = "sqlite:///./sitelens.db"

    # Comma-separated list of origins allowed to call this API.
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
