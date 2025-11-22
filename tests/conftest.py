"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import os

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"

from src.orchestrator.models import LLMResponse, LLMProvider, QueryType


@pytest.fixture
def mock_gpt_response():
    """Mock GPT response."""
    return {
        "content": "This is a GPT-4o response about solar panels.",
        "tokens_used": 150,
        "model": "gpt-4o",
        "finish_reason": "stop",
        "metadata": {
            "prompt_tokens": 50,
            "completion_tokens": 100,
        },
    }


@pytest.fixture
def mock_claude_response():
    """Mock Claude response."""
    return {
        "content": "This is a Claude 3.5 response about solar panels.",
        "tokens_used": 160,
        "model": "claude-3-5-sonnet-20241022",
        "stop_reason": "end_turn",
        "metadata": {
            "input_tokens": 55,
            "output_tokens": 105,
        },
    }


@pytest.fixture
def sample_llm_response_gpt():
    """Sample LLM response from GPT."""
    return LLMResponse(
        provider=LLMProvider.GPT,
        content="GPT response content",
        model="gpt-4o",
        tokens_used=150,
        latency_ms=500.0,
    )


@pytest.fixture
def sample_llm_response_claude():
    """Sample LLM response from Claude."""
    return LLMResponse(
        provider=LLMProvider.CLAUDE,
        content="Claude response content",
        model="claude-3-5-sonnet-20241022",
        tokens_used=160,
        latency_ms=550.0,
    )


@pytest.fixture
def mock_gpt_client():
    """Mock GPT client."""
    client = AsyncMock()
    client.generate = AsyncMock()
    client.generate_with_image = AsyncMock()
    return client


@pytest.fixture
def mock_claude_client():
    """Mock Claude client."""
    client = AsyncMock()
    client.generate = AsyncMock()
    client.generate_with_image = AsyncMock()
    return client
