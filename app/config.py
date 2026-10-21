from enum import Enum

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageBackend(str, Enum):
    DATABASE = "database"
    MEMORY = "memory"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    storage_backend: StorageBackend = StorageBackend.DATABASE
    database_url: str = Field(
        default="postgresql+psycopg://postgres:change-me@localhost:5432/library",
        description="SQLAlchemy PostgreSQL connection URL",
    )
    database_echo_sql: bool = False

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use the postgresql+psycopg:// scheme")
        return value
