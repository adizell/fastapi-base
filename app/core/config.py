# app/core/config.py
"""
Application Configuration Module
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    VERSION: str = "1.0.0"
    PROJECT_NAME: str = "FastAPI Project"
    PROJECT_DESCRIPTION: str = "Modern FastAPI project template with authentication and authorization"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: List[AnyHttpUrl] = []
    INITIALIZE_DB: bool = False
    FIRST_SUPERUSER_EMAIL: Optional[str] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = 6379
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v

        values = info.data

        db_user = values.get("POSTGRES_USER")
        db_password = values.get("POSTGRES_PASSWORD")
        db_host = values.get("POSTGRES_SERVER")
        db_port = values.get("POSTGRES_PORT")
        db_name = values.get("POSTGRES_DB")

        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("Faltam variáveis para montar a conexão com o banco de dados")

        return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings()

if __name__ == "__main__":
    import json

    print("✅ Variáveis carregadas:")
    print(json.dumps(settings.model_dump(), indent=4))
