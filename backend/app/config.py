"""
Configuration management for Solar PV LLM AI
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    debug: bool = True

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-sonnet-20240229"
    anthropic_max_tokens: int = 4000

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "solar-pv-embeddings"
    pinecone_dimension: int = 1536

    # NREL
    nrel_api_key: str = ""
    nrel_base_url: str = "https://developer.nrel.gov/api"

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/solar_pv_db"
    postgres_user: str = "solar_user"
    postgres_password: str = ""
    postgres_db: str = "solar_pv_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    # Security
    jwt_secret: str = ""
    jwt_expiration: int = 3600
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # AI/ML
    embedding_model: str = "text-embedding-ada-002"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_context_length: int = 8000

    # RAG
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.7
    enable_citations: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
