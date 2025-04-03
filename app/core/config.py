"""
Application Configuration Module

This module loads and manages application configuration from environment variables.
It uses Pydantic's Settings class to validate configuration values.
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Inherits from Pydantic's BaseSettings to automatically parse environment variables.
    """
    # API configuration
    API_PREFIX: str = "/api"
    VERSION: str = "1.0.0"

    # Project metadata
    PROJECT_NAME: str = "FastAPI Project"
    PROJECT_DESCRIPTION: str = "Modern FastAPI project template with authentication and authorization"

    # Environment and debug settings
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS configuration
    CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database initialization flag
    INITIALIZE_DB: bool = False

    # Super admin creation (optional)
    FIRST_SUPERUSER_EMAIL: Optional[str] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None

    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Redis settings (optional, for rate limiting, caching, etc.)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = 6379

    # Rate limiting settings
    RATE_LIMIT_PER_MINUTE: int = 60

    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        """
        Assemble database connection string from individual components.

        Args:
            v: Value of SQLALCHEMY_DATABASE_URI if set directly
            info: Values of other fields in the model

        Returns:
            Database connection string
        """
        if isinstance(v, str):
            return v

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", 5432)),
            path=values.get("POSTGRES_DB"),
            # path=f"{values.get('POSTGRES_DB') or ''}",
        )

    # @field_validator("CORS_ORIGINS", mode="before")
    # def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
    #     """
    #     Parse CORS_ORIGINS from string to list if needed.
    #
    #     Args:
    #         v: CORS origins as string or list
    #
    #     Returns:
    #         List of CORS origins
    #     """
    #     if isinstance(v, str) and not v.startswith("["):
    #         return [i.strip() for i in v.split(",")]
    #     elif isinstance(v, (list, str)):
    #         return v
    #     raise ValueError(v)


# Create settings instance
settings = Settings()
