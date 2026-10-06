"""
Rawbank Sentient Fraud Intelligence Platform
Backend Configuration Settings
-----------------------------------------------------------------------------
Manages application configuration, environment settings, and database path.
Zero secrets in source code.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


# Base project root: 2 levels up from backend/app -> repo root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = Field(default="Rawbank Sentient Fraud Intelligence Platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")

    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Database
    database_path_raw: str = Field(default="database/synthetic_bank.db", alias="DATABASE_PATH")

    # CORS
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS"
    )

    # Pagination
    default_page_size: int = Field(default=25, alias="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, alias="MAX_PAGE_SIZE")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Phase 6: Copilot / Groq LLM Configuration
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    groq_api_url: str = Field(default="https://api.groq.com/openai/v1/chat/completions", alias="GROQ_API_URL")
    groq_timeout_seconds: float = Field(default=30.0, alias="GROQ_TIMEOUT_SECONDS")
    copilot_use_mock: bool = Field(default=False, alias="COPILOT_USE_MOCK")

    @property
    def database_path(self) -> Path:
        """Resolve database path relative to project root if not absolute."""
        p = Path(self.database_path_raw)
        if p.is_absolute():
            return p
        return BASE_DIR / p

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
