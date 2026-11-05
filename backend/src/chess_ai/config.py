from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable override."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Chess AI Tutor API"
    APP_ENV: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/chess_ai",
        description="Async PostgreSQL connection string",
    )

    # Redis Cache & Queue
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and task broker",
    )

    # Stockfish Engine
    STOCKFISH_PATH: str = Field(
        default="stockfish",
        description="Path or binary name of the Stockfish UCI engine",
    )
    STOCKFISH_DEFAULT_DEPTH: int = 18
    STOCKFISH_ANALYSIS_THREADS: int = 2
    STOCKFISH_MAX_CONCURRENT_ENGINES: int = 4

    # LLM Tutor Provider
    LLM_PROVIDER: Literal["gemini", "openai", "anthropic", "mock"] = "mock"
    LLM_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gemini-1.5-pro"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
