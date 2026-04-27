from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "TraditionalRag API"
    app_env: str = "dev"
    api_prefix: str = "/v1"
    log_level: str = "INFO"

    data_dir: str = "data"
    persist_dir: str = "faiss_store"

    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama-3.1-8b-instant"
    groq_api_key: str = ""

    admin_api_key: str = ""
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_bucket: str = "pdfs"
    supabase_table: str = "documents"
    supabase_upload_prefix: str = "pdfs"
    supabase_public_bucket: bool = True
    max_upload_mb: int = 50

    skip_startup_init: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
