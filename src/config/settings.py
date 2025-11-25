"""Configuration settings for Solar PV LLM AI"""

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Pinecone Configuration
    PINECONE_API_KEY: str = Field(..., description="Pinecone API key")
    PINECONE_INDEX_NAME: str = Field(
        default="solar-pv-index",
        description="Pinecone index name"
    )
    PINECONE_ENVIRONMENT: str = Field(
        default="us-east-1",
        description="Pinecone environment"
    )

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-large",
        description="OpenAI embedding model"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=1536,
        description="Embedding vector dimension"
    )

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_TITLE: str = Field(default="Solar PV LLM AI", description="API title")
    API_VERSION: str = Field(default="0.1.0", description="API version")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="standard", description="Log format (standard or json)")

    # Vector Store Configuration
    BATCH_SIZE: int = Field(default=100, description="Batch size for upsert operations")
    MAX_RETRIES: int = Field(default=3, description="Maximum retry attempts")
    RETRY_DELAY: float = Field(default=1.0, description="Delay between retries in seconds")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
