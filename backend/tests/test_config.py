"""
Tests for configuration management
"""
import os
import pytest
from app.config import Settings


def test_settings_default_values():
    """Test that settings have correct default values"""
    settings = Settings()

    assert settings.app_env in ["development", "staging", "production"]
    assert settings.app_port > 0
    assert settings.openai_model in ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    assert settings.anthropic_model.startswith("claude")
    assert settings.pinecone_dimension == 1536


def test_settings_from_env(monkeypatch):
    """Test that settings load from environment variables"""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("DEBUG", "false")

    settings = Settings()

    assert settings.app_env == "production"
    assert settings.app_port == 9000
    assert settings.debug is False


def test_rag_settings():
    """Test RAG configuration settings"""
    settings = Settings()

    assert settings.rag_top_k > 0
    assert 0.0 <= settings.rag_similarity_threshold <= 1.0
    assert isinstance(settings.enable_citations, bool)


def test_database_url_format():
    """Test database URL has correct format"""
    settings = Settings()

    assert settings.database_url.startswith("postgresql://")
    assert settings.postgres_port == 5432


def test_embedding_settings():
    """Test embedding model settings"""
    settings = Settings()

    assert settings.chunk_size > 0
    assert settings.chunk_overlap >= 0
    assert settings.chunk_overlap < settings.chunk_size
    assert settings.max_context_length > 0
