from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "ERP MBG Backend"
    app_env: str = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"

    database_url: str | None = None
    database_sync_url: str | None = None
    database_pool_size: int = 20
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    database_echo: bool = False

    jwt_secret_key: str = Field(
        default="replace-with-long-random-secret-minimum-32-characters",
        min_length=32,
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    cors_allowed_origins: list[str] = []
    cors_allow_credentials: bool = True
    cors_allowed_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    cors_allowed_headers: list[str] = [
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "X-Tenant-ID",
        "X-SPPG-ID",
    ]

    default_timezone: str = "Asia/Jakarta"
    default_currency: str = "IDR"

    openai_enabled: bool = False
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_nl2sql_model: str | None = None
    openai_timeout_seconds: int = 60
    openai_nl2sql_allow_execution: bool = False
    openai_nl2sql_max_rows: int = 200
    openai_nl2sql_system_prompt: str = (
        "You translate analytical business questions into safe PostgreSQL SELECT queries for ERP MBG. "
        "Return JSON only with keys: sql, explanation, assumptions, safety_notes."
    )

    google_ai_enabled: bool = False
    google_ai_api_key: str | None = None
    google_ai_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    google_ai_media_model: str | None = None
    google_ai_timeout_seconds: int = 120
    google_ai_media_max_download_mb: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
