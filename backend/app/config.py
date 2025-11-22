"""
Solar PV LLM AI - Configuration Management

This module provides centralized configuration management with:
- Environment variable loading and validation
- Type coercion and default values
- Required vs optional field distinction
- Configuration validation on startup
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from functools import lru_cache


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


@dataclass
class LLMConfig:
    """LLM API configuration."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None

    def has_any_llm_key(self) -> bool:
        """Check if at least one LLM API key is configured."""
        return any([
            self.openai_api_key,
            self.anthropic_api_key,
            self.google_api_key
        ])

    def get_available_providers(self) -> List[str]:
        """Return list of configured LLM providers."""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_api_key:
            providers.append("google")
        return providers


@dataclass
class PineconeConfig:
    """Pinecone vector database configuration."""
    api_key: Optional[str] = None
    environment: str = "us-west-2"
    index_name: str = "pv-expert-knowledge"
    namespace: str = "solar-pv-docs"

    def is_configured(self) -> bool:
        """Check if Pinecone is properly configured."""
        return bool(self.api_key and self.index_name)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    database_url: str = "postgresql://postgres:password@localhost:5432/solar_pv_ai"
    redis_url: str = "redis://localhost:6379/0"

    def get_async_database_url(self) -> str:
        """Convert sync database URL to async (asyncpg)."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url


@dataclass
class RAGConfig:
    """RAG (Retrieval-Augmented Generation) configuration."""
    embedding_model: str = "text-embedding-3-small"
    default_llm_model: str = "gpt-4-turbo-preview"
    max_tokens: int = 4096
    temperature: float = 0.7
    top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8080"])


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    per_minute: int = 60
    per_hour: int = 1000


@dataclass
class FeatureFlags:
    """Feature flags configuration."""
    enable_citations: bool = True
    enable_cache: bool = True
    enable_autonomous_agent: bool = False


@dataclass
class Settings:
    """Main application settings container."""

    # Sub-configurations
    llm: LLMConfig = field(default_factory=LLMConfig)
    pinecone: PineconeConfig = field(default_factory=PineconeConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)

    # Application settings
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    secret_key: str = ""

    # External APIs
    nrel_api_key: Optional[str] = None

    # Monitoring
    sentry_dsn: Optional[str] = None
    otel_endpoint: Optional[str] = None

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


def _get_env(key: str, default: str = "") -> str:
    """Get environment variable with default."""
    return os.getenv(key, default).strip()


def _get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    value = os.getenv(key, str(default)).strip().lower()
    return value in ("true", "1", "yes", "on")


def _get_env_int(key: str, default: int) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def _get_env_float(key: str, default: float) -> float:
    """Get float environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


def _get_env_list(key: str, default: List[str] = None) -> List[str]:
    """Get list environment variable (comma-separated)."""
    if default is None:
        default = []
    value = os.getenv(key, "").strip()
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def load_settings() -> Settings:
    """Load settings from environment variables."""

    # Load LLM configuration
    llm_config = LLMConfig(
        openai_api_key=_get_env("OPENAI_API_KEY") or None,
        anthropic_api_key=_get_env("ANTHROPIC_API_KEY") or None,
        google_api_key=_get_env("GOOGLE_API_KEY") or None,
        cohere_api_key=_get_env("COHERE_API_KEY") or None,
    )

    # Load Pinecone configuration
    pinecone_config = PineconeConfig(
        api_key=_get_env("PINECONE_API_KEY") or None,
        environment=_get_env("PINECONE_ENVIRONMENT", "us-west-2"),
        index_name=_get_env("PINECONE_INDEX_NAME", "pv-expert-knowledge"),
        namespace=_get_env("PINECONE_NAMESPACE", "solar-pv-docs"),
    )

    # Load Database configuration
    database_config = DatabaseConfig(
        database_url=_get_env("DATABASE_URL", "postgresql://postgres:password@localhost:5432/solar_pv_ai"),
        redis_url=_get_env("REDIS_URL", "redis://localhost:6379/0"),
    )

    # Load RAG configuration
    rag_config = RAGConfig(
        embedding_model=_get_env("EMBEDDING_MODEL", "text-embedding-3-small"),
        default_llm_model=_get_env("DEFAULT_LLM_MODEL", "gpt-4-turbo-preview"),
        max_tokens=_get_env_int("MAX_TOKENS", 4096),
        temperature=_get_env_float("LLM_TEMPERATURE", 0.7),
        top_k=_get_env_int("RAG_TOP_K", 5),
        chunk_size=_get_env_int("CHUNK_SIZE", 1000),
        chunk_overlap=_get_env_int("CHUNK_OVERLAP", 200),
    )

    # Load Server configuration
    server_config = ServerConfig(
        host=_get_env("API_HOST", "0.0.0.0"),
        port=_get_env_int("API_PORT", 8000),
        cors_origins=_get_env_list("CORS_ORIGINS", ["http://localhost:3000", "http://localhost:8080"]),
    )

    # Load Rate Limit configuration
    rate_limit_config = RateLimitConfig(
        per_minute=_get_env_int("RATE_LIMIT_PER_MINUTE", 60),
        per_hour=_get_env_int("RATE_LIMIT_PER_HOUR", 1000),
    )

    # Load Feature Flags
    feature_flags = FeatureFlags(
        enable_citations=_get_env_bool("ENABLE_CITATIONS", True),
        enable_cache=_get_env_bool("ENABLE_CACHE", True),
        enable_autonomous_agent=_get_env_bool("ENABLE_AUTONOMOUS_AGENT", False),
    )

    return Settings(
        llm=llm_config,
        pinecone=pinecone_config,
        database=database_config,
        rag=rag_config,
        server=server_config,
        rate_limit=rate_limit_config,
        features=feature_flags,
        debug=_get_env_bool("DEBUG", False),
        log_level=_get_env("LOG_LEVEL", "INFO"),
        environment=_get_env("ENVIRONMENT", "development"),
        secret_key=_get_env("SECRET_KEY", ""),
        nrel_api_key=_get_env("NREL_API_KEY") or None,
        sentry_dsn=_get_env("SENTRY_DSN") or None,
        otel_endpoint=_get_env("OTEL_EXPORTER_OTLP_ENDPOINT") or None,
    )


def validate_settings(settings: Settings, strict: bool = False) -> List[str]:
    """
    Validate settings and return list of warnings/errors.

    Args:
        settings: Settings object to validate
        strict: If True, raise ConfigurationError on critical issues

    Returns:
        List of warning messages
    """
    warnings = []
    errors = []

    # Check LLM API keys
    if not settings.llm.has_any_llm_key():
        errors.append("No LLM API keys configured. At least one of OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY is required.")

    # Check Pinecone configuration
    if not settings.pinecone.is_configured():
        warnings.append("Pinecone not configured. Vector search features will be unavailable.")

    # Check secret key in production
    if settings.is_production():
        if not settings.secret_key:
            errors.append("SECRET_KEY must be set in production environment.")
        if settings.debug:
            errors.append("DEBUG must be False in production environment.")

    # Check NREL API key
    if not settings.nrel_api_key:
        warnings.append("NREL_API_KEY not configured. Solar resource data features will be unavailable.")

    # Check database URL
    if "password" in settings.database.database_url and settings.is_production():
        warnings.append("Database URL appears to contain a plaintext password. Consider using environment-specific secrets management.")

    # Validate RAG configuration
    if settings.rag.chunk_overlap >= settings.rag.chunk_size:
        errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE.")

    if settings.rag.temperature < 0 or settings.rag.temperature > 1:
        errors.append("LLM_TEMPERATURE must be between 0 and 1.")

    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if settings.log_level.upper() not in valid_log_levels:
        errors.append(f"Invalid LOG_LEVEL. Must be one of: {', '.join(valid_log_levels)}")

    if strict and errors:
        raise ConfigurationError("\n".join(errors))

    return warnings + errors


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).

    This function loads settings from environment variables and caches the result.
    Call this function to access settings throughout the application.
    """
    return load_settings()


def print_config_status(settings: Settings = None) -> None:
    """Print configuration status for debugging."""
    if settings is None:
        settings = get_settings()

    print("\n" + "=" * 60)
    print("Solar PV LLM AI - Configuration Status")
    print("=" * 60)

    print(f"\nEnvironment: {settings.environment}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")

    print("\nLLM Providers:")
    providers = settings.llm.get_available_providers()
    if providers:
        for provider in providers:
            print(f"  - {provider}: configured")
    else:
        print("  - None configured!")

    if settings.llm.cohere_api_key:
        print("  - cohere (embeddings): configured")

    print(f"\nPinecone: {'configured' if settings.pinecone.is_configured() else 'not configured'}")
    if settings.pinecone.is_configured():
        print(f"  - Environment: {settings.pinecone.environment}")
        print(f"  - Index: {settings.pinecone.index_name}")

    print(f"\nNREL API: {'configured' if settings.nrel_api_key else 'not configured'}")

    print(f"\nServer: {settings.server.host}:{settings.server.port}")
    print(f"CORS Origins: {', '.join(settings.server.cors_origins)}")

    print("\nFeature Flags:")
    print(f"  - Citations: {settings.features.enable_citations}")
    print(f"  - Cache: {settings.features.enable_cache}")
    print(f"  - Autonomous Agent: {settings.features.enable_autonomous_agent}")

    # Validate and show warnings
    warnings = validate_settings(settings)
    if warnings:
        print("\nWarnings/Errors:")
        for warning in warnings:
            print(f"  ! {warning}")

    print("\n" + "=" * 60 + "\n")


# Export commonly used items
__all__ = [
    "Settings",
    "LLMConfig",
    "PineconeConfig",
    "DatabaseConfig",
    "RAGConfig",
    "ServerConfig",
    "RateLimitConfig",
    "FeatureFlags",
    "ConfigurationError",
    "get_settings",
    "load_settings",
    "validate_settings",
    "print_config_status",
]
