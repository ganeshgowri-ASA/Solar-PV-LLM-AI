"""
Configuration management for Solar PV LLM AI System
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_version: str = Field(default="v1", env="API_VERSION")
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    debug: bool = Field(default=False, env="DEBUG")

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # Vector Store Configuration
    vector_store_type: str = Field(default="pinecone", env="VECTOR_STORE_TYPE")
    vector_store_url: Optional[str] = Field(default=None, env="VECTOR_STORE_URL")
    vector_store_api_key: Optional[str] = Field(default=None, env="VECTOR_STORE_API_KEY")
    vector_store_index_name: str = Field(default="solar-pv-knowledge", env="VECTOR_STORE_INDEX_NAME")
    vector_dimension: int = Field(default=1536, env="VECTOR_DIMENSION")  # OpenAI ada-002 dimension

    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")
    llm_model: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL")
    llm_api_key: str = Field(..., env="LLM_API_KEY")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")
    llm_top_p: float = Field(default=1.0, env="LLM_TOP_P")

    # Embedding Configuration
    embedding_provider: str = Field(default="openai", env="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    embedding_batch_size: int = Field(default=100, env="EMBEDDING_BATCH_SIZE")

    # RAG Configuration
    rag_top_k: int = Field(default=5, env="RAG_TOP_K")
    rag_similarity_threshold: float = Field(default=0.7, env="RAG_SIMILARITY_THRESHOLD")
    rag_chunk_size: int = Field(default=1000, env="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=200, env="RAG_CHUNK_OVERLAP")

    # Feedback Configuration
    feedback_confidence_threshold: float = Field(default=0.8, env="FEEDBACK_CONFIDENCE_THRESHOLD")
    feedback_negative_rating_threshold: float = Field(default=2.0, env="FEEDBACK_NEGATIVE_RATING_THRESHOLD")
    feedback_review_batch_size: int = Field(default=50, env="FEEDBACK_REVIEW_BATCH_SIZE")

    # Retraining Configuration
    retraining_enabled: bool = Field(default=True, env="RETRAINING_ENABLED")
    retraining_schedule_cron: str = Field(default="0 2 * * 0", env="RETRAINING_SCHEDULE_CRON")  # Weekly at 2 AM Sunday
    retraining_min_feedback_count: int = Field(default=100, env="RETRAINING_MIN_FEEDBACK_COUNT")
    retraining_checkpoint_dir: str = Field(default="./data/model_checkpoints", env="RETRAINING_CHECKPOINT_DIR")

    # LoRA Fine-tuning Configuration
    lora_r: int = Field(default=8, env="LORA_R")
    lora_alpha: int = Field(default=16, env="LORA_ALPHA")
    lora_dropout: float = Field(default=0.1, env="LORA_DROPOUT")
    lora_target_modules: List[str] = Field(default=["q_proj", "v_proj"], env="LORA_TARGET_MODULES")

    # Training Configuration
    training_batch_size: int = Field(default=4, env="TRAINING_BATCH_SIZE")
    training_epochs: int = Field(default=3, env="TRAINING_EPOCHS")
    training_learning_rate: float = Field(default=2e-4, env="TRAINING_LEARNING_RATE")
    training_gradient_accumulation_steps: int = Field(default=4, env="TRAINING_GRADIENT_ACCUMULATION_STEPS")

    # Celery Configuration (Task Queue)
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    celery_task_track_started: bool = Field(default=True, env="CELERY_TASK_TRACK_STARTED")

    # Security Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")

    # Admin Configuration
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")
    admin_password_hash: str = Field(..., env="ADMIN_PASSWORD_HASH")
    allow_registration: bool = Field(default=False, env="ALLOW_REGISTRATION")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    # Monitoring Configuration
    enable_prometheus: bool = Field(default=True, env="ENABLE_PROMETHEUS")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")

    # File Storage Configuration
    data_dir: str = Field(default="./data", env="DATA_DIR")
    upload_max_size_mb: int = Field(default=50, env="UPLOAD_MAX_SIZE_MB")

    @validator("vector_store_type")
    def validate_vector_store(cls, v):
        valid_stores = ["pinecone", "weaviate", "chromadb", "qdrant", "faiss"]
        if v not in valid_stores:
            raise ValueError(f"vector_store_type must be one of {valid_stores}")
        return v

    @validator("llm_provider")
    def validate_llm_provider(cls, v):
        valid_providers = ["openai", "anthropic", "azure", "huggingface"]
        if v not in valid_providers:
            raise ValueError(f"llm_provider must be one of {valid_providers}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global settings
    if settings is None:
        settings = Settings()
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global settings
    settings = Settings()
    return settings
