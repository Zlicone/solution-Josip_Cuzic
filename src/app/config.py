"""Konfiguracija aplikacije (pydantic-settings).

Sve vrijednosti se mogu nadjačati preko env varijabli ili .env datoteke.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Aplikacija
    app_name: str = "TicketHub"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"

    # Baza
    database_url: str = "sqlite+aiosqlite:///./tickethub.db"

    # Vanjski izvor (DummyJSON)
    dummyjson_base_url: str = "https://dummyjson.com"
    http_timeout: float = 10.0

    # Sync
    seed_on_startup: bool = False

    # Auth (koristi se od auth commita nadalje)
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Cache (koristi se od caching commita nadalje)
    cache_ttl_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    """Cachirani singleton postavki (jednom se čita env, svugdje se dijeli)."""
    return Settings()


settings = get_settings()
