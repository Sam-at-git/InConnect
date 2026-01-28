"""
Application configuration using Pydantic settings
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="inconnect", alias="APP_NAME")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    debug: bool = Field(default=False, alias="DEBUG")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Database (SQLite by default)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/inconnect.db", alias="DATABASE_URL"
    )

    # JWT
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # WeChat
    wechat_corp_id: str = Field(default="", alias="WECHAT_CORP_ID")
    wechat_app_secret: str = Field(default="", alias="WECHAT_APP_SECRET")
    wechat_agent_id: int = Field(default=0, alias="WECHAT_AGENT_ID")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
