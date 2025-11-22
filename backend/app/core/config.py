"""
Application Configuration
Centralized settings management using Pydantic
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project
    PROJECT_NAME: str = "Solar PV LLM AI"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # API
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    API_RELOAD: bool = Field(default=False, env="API_RELOAD")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_MINUTES: int = Field(default=60, env="JWT_EXPIRATION_MINUTES")
    API_KEY_HEADER: str = Field(default="X-API-Key", env="API_KEY_HEADER")

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        env="CORS_ORIGINS"
    )

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_CACHE_URL: str = Field(..., env="REDIS_CACHE_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # ML Models
    MODEL_PATH: str = Field(default="/app/models", env="MODEL_PATH")
    MODEL_CACHE_DIR: str = Field(default="/app/cache/models", env="MODEL_CACHE_DIR")
    TRAINING_BATCH_SIZE: int = Field(default=32, env="TRAINING_BATCH_SIZE")
    LEARNING_RATE: float = Field(default=0.001, env="LEARNING_RATE")
    MAX_EPOCHS: int = Field(default=100, env="MAX_EPOCHS")
    EARLY_STOPPING_PATIENCE: int = Field(default=10, env="EARLY_STOPPING_PATIENCE")
    DEVICE: str = Field(default="cpu", env="DEVICE")

    # RAG
    RAG_MODEL: str = Field(default="text-embedding-ada-002", env="RAG_MODEL")
    RAG_CHUNK_SIZE: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    RAG_CHUNK_OVERLAP: int = Field(default=200, env="RAG_CHUNK_OVERLAP")
    RAG_TOP_K: int = Field(default=5, env="RAG_TOP_K")
    VECTOR_DB_TYPE: str = Field(default="pgvector", env="VECTOR_DB_TYPE")
    VECTOR_DB_URL: str = Field(default="localhost:6333", env="VECTOR_DB_URL")
    VECTOR_DB_API_KEY: Optional[str] = Field(default=None, env="VECTOR_DB_API_KEY")

    # LLM
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")
    LLM_MODEL: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")

    # External APIs
    WEATHER_API_KEY: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    WEATHER_API_URL: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        env="WEATHER_API_URL"
    )
    NREL_API_KEY: Optional[str] = Field(default=None, env="NREL_API_KEY")

    # Celery
    CELERY_BROKER_URL: str = Field(..., env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(..., env="CELERY_RESULT_BACKEND")
    CELERY_TASK_SERIALIZER: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    CELERY_RESULT_SERIALIZER: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    CELERY_ACCEPT_CONTENT: str = Field(default="json", env="CELERY_ACCEPT_CONTENT")
    CELERY_TIMEZONE: str = Field(default="UTC", env="CELERY_TIMEZONE")

    # Storage
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")
    S3_BUCKET: Optional[str] = Field(default=None, env="S3_BUCKET")
    S3_REGION: str = Field(default="us-east-1", env="S3_REGION")
    S3_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="S3_SECRET_ACCESS_KEY")
    S3_ENDPOINT_URL: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    LOCAL_STORAGE_PATH: str = Field(default="/app/data/storage", env="LOCAL_STORAGE_PATH")

    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # Feature Flags
    ENABLE_INCREMENTAL_TRAINING: bool = Field(default=True, env="ENABLE_INCREMENTAL_TRAINING")
    ENABLE_CITATION_TRACKING: bool = Field(default=True, env="ENABLE_CITATION_TRACKING")
    ENABLE_AUTONOMOUS_DELIVERY: bool = Field(default=True, env="ENABLE_AUTONOMOUS_DELIVERY")
    ENABLE_RATE_LIMITING: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
