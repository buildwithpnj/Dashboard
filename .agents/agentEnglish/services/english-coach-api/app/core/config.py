import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine monorepo workspace root (4 levels up from this app/core file)
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CORE_DIR))))

class Settings(BaseSettings):
    # Application configurations
    APP_NAME: str = "Warborn English Coach API"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Hardening V3.5 Authentication & Tenancy Settings
    AUTH_ENABLED: bool = False
    ADMIN_API_KEY: str = "warborn_admin_secret"
    JWT_SECRET_KEY: str = "super_jwt_secret_key"
    DEFAULT_TENANT_ID: str = "default_tenant"
    
    # Hardening V4 Celery Task Queue Settings
    CELERY_ENABLED: bool = False
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Database configuration (Async SQLite or PostgreSQL)
    DATABASE_URL: str = "sqlite+aiosqlite:///warborn.db"

    # Engine variables
    MODEL_PROVIDER: str = "mock"
    MODEL_NAME: str = "gpt-4o-mini"
    EVAL_MODE: str = "mock"
    
    # Credentials & API state configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ENABLED: bool = False
    GEMINI_API_KEY: Optional[str] = None

    # Performance / optimization limits
    REQUEST_TIMEOUT_SECONDS: int = 15
    MAX_RETRIES: int = 1
    MAX_COMPLETION_TOKENS: int = 180
    MAX_RETRIEVED_MEMORIES: int = 3
    MAX_DYNAMIC_CONTEXT_TOKENS: int = 500
    APPROVED_EXAMPLES_FILE: str = os.path.join(WORKSPACE_ROOT, "data", "approved", "approved_examples.jsonl")
    LOG_LEVEL: str = "INFO"

    # V8 Large-Scale Dataset Eval Settings
    MAX_EVAL_EXAMPLES_PER_RUN: int = 1000
    MAX_EVAL_BUDGET_USD: float = 5.0
    EVAL_BATCH_SIZE: int = 50
    PREMIUM_MODEL_NAME: str = "gpt-4o"
    CHEAP_MODEL_NAME: str = "gpt-3.5-turbo"
    PREMIUM_TIER_CAP_PCT: int = 5
    GOLD_PROMOTION_THRESHOLD: float = 0.85
    HF_CACHE_DIR: str = os.path.join(WORKSPACE_ROOT, "data", "hf_cache")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
