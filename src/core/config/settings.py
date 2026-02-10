"""Application settings and configuration."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Nevo", description="Application name")
    app_env: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(..., description="Application secret key")
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database - Supabase PostgreSQL
    database_url: str = Field(
        ..., description="Supabase PostgreSQL connection URL (postgresql+asyncpg://...)"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    supabase_url: str = Field(
        default="", description="Supabase project URL (optional, for direct API access)"
    )
    supabase_key: str = Field(
        default="", description="Supabase anon/service key (optional)"
    )

    # Redis Cache - Upstash
    redis_url: str = Field(
        default="",
        description="Redis connection URL (Upstash REST endpoint or standard redis:// URL)",
    )
    upstash_rest_token: str = Field(
        default="",
        description="Upstash REST API token (required if using Upstash REST API)",
    )
    redis_enabled: bool = Field(default=True, description="Enable Redis caching")

    # JWT
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration in days"
    )

    # AI - Google Gemini
    google_api_key: str = Field(default="", description="Google API key for Gemini")
    gemini_model: str = Field(default="gemini-pro", description="Gemini model name")

    # AI - Local Model (Ollama)
    local_ai_enabled: bool = Field(
        default=False, description="Enable local AI model (Ollama)"
    )
    local_ai_url: str = Field(
        default="http://localhost:11434", description="Ollama API URL"
    )
    local_ai_model: str = Field(
        default="llama3.2",
        description="Local AI model name (e.g., llama3.2, mistral, qwen2.5)",
    )

    # AI - OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")

    # AWS S3
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")
    aws_region: str = Field(default="us-east-1", description="AWS region")
    s3_bucket_name: str = Field(default="nevo-lessons", description="S3 bucket name")

    # GCP Storage
    gcp_project_id: str = Field(default="", description="GCP project ID")
    gcs_bucket_name: str = Field(default="nevo-lessons", description="GCS bucket name")

    # Email - Resend
    resend_api_key: str = Field(..., description="Resend API key")
    email_from: str = Field(
        default="noreply@nevolearning.com",
        description="Email from address (must be verified in Resend)",
    )

    # Celery
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1", description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", description="Celery result backend"
    )

    # Frontend
    frontend_url: str = Field(
        default="http://localhost:3000",
        description="Frontend application URL for email links",
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.app_env == "testing"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
