"""Configuration management for the LLM Orchestrator."""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Model Configuration
    gpt_model: str = "gpt-4o"
    claude_model: str = "claude-3-5-sonnet-20241022"

    # Orchestrator Configuration
    default_llm: Literal["auto", "gpt", "claude"] = "auto"
    enable_fallback: bool = True
    enable_hybrid_synthesis: bool = True
    classification_threshold: float = 0.7

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Timeouts (seconds)
    llm_timeout: int = 60
    max_retries: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
