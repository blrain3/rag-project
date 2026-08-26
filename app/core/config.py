"""Application configuration.

All runtime settings are loaded from environment variables (and the local
`.env` file) through pydantic-settings. No module in this project should
read `os.environ` directly -- everything goes through `get_settings()`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central, typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "Personal RAG Knowledge Base"
    app_env: str = "development"
    debug: bool = True

    # --- Database (PostgreSQL + pgvector) ---
    database_url: str = "postgresql://postgres:postgres@localhost:5432/rag"

    # --- LLM (OpenAI-compatible API) ---
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    # --- Embedding ---
    embedding_model: str = "BAAI/bge-m3"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (created once per process)."""
    return Settings()
