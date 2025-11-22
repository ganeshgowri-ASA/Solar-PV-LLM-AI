"""
Application configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str = Field(default="Solar PV LLM AI")
    APP_VERSION: str = Field(default="1.0.0")
    APP_DESCRIPTION: str = Field(default="Solar PV AI System with RAG and LLM")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    # Server Settings
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # Security & Authentication
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    API_KEY: str = Field(default="dev-api-key")

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")

    # Anthropic Configuration
    ANTHROPIC_API_KEY: str = Field(default="")

    # Vector Database Configuration
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./data/chroma")
    CHROMA_COLLECTION_NAME: str = Field(default="solar_pv_documents")

    # RAG Configuration
    MAX_RETRIEVAL_RESULTS: int = Field(default=5)
    CHUNK_SIZE: int = Field(default=1000)
    CHUNK_OVERLAP: int = Field(default=200)

    # Image Analysis Configuration
    DEFECT_DETECTION_MODEL_PATH: str = Field(default="./models/defect_detector.pth")
    IMAGE_UPLOAD_DIR: str = Field(default="./data/uploads/images")
    MAX_IMAGE_SIZE_MB: int = Field(default=10)

    # Document Ingestion Configuration
    DOCUMENT_UPLOAD_DIR: str = Field(default="./data/uploads/documents")
    SUPPORTED_FORMATS: str = Field(default="pdf,docx,txt")
    MAX_DOCUMENT_SIZE_MB: int = Field(default=50)

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="./logs/app.log")

    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./data/solar_pv.db")

    # CORS Configuration
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: str = Field(default="*")
    CORS_ALLOW_HEADERS: str = Field(default="*")

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def supported_formats_list(self) -> List[str]:
        """Parse supported document formats from comma-separated string."""
        return [fmt.strip() for fmt in self.SUPPORTED_FORMATS.split(",")]


# Global settings instance
settings = Settings()
