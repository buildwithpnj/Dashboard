import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://personal_os:personal_os_dev@localhost:5432/personal_os"
    )

    def __init__(self, **values):
        super().__init__(**values)
        # Robust fallback: fetch directly from host environment variables
        env_db_url = (
            os.environ.get("DATABASE_URL") or 
            os.environ.get("DATABASE_PRIVATE_URL") or 
            os.environ.get("database_url")
        )
        if env_db_url:
            self.database_url = env_db_url

        if self.database_url:
            # Clean trailing/leading whitespace and quotes
            self.database_url = self.database_url.strip().strip('"').strip("'")
            
            # Standardize scheme for asyncpg
            if self.database_url.startswith("postgres://"):
                self.database_url = self.database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif self.database_url.startswith("postgresql://"):
                self.database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-me-to-a-random-64-char-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Google Drive Integration
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str = "http://localhost:3000/storage/callback"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"


settings = Settings()
