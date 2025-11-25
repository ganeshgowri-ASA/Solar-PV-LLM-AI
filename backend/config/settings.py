"""
Application configuration settings using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # NREL API Configuration
    nrel_api_key: str = Field(default="DEMO_KEY", description="NREL API Key")
    nrel_api_base_url: str = Field(
        default="https://developer.nrel.gov/api",
        description="NREL API Base URL"
    )

    # Application Settings
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API Settings
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    project_name: str = Field(
        default="Solar PV LLM AI System",
        description="Project name"
    )
    version: str = Field(default="1.0.0", description="API version")

    # CORS Settings
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Allowed CORS origins (comma-separated)"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
