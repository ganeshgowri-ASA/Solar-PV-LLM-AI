"""
Tests for chat endpoint.
"""
import pytest
from fastapi.testclient import TestClient


def test_chat_endpoint(client: TestClient, auth_headers: dict, sample_chat_request: dict):
    """Test chat endpoint with RAG."""
    response = client.post(
        "/chat/",
        json=sample_chat_request,
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert "citations" in data
    assert "tokens_used" in data
    assert "processing_time" in data

    assert isinstance(data["response"], str)
    assert isinstance(data["citations"], list)
    assert isinstance(data["tokens_used"], int)
    assert data["processing_time"] > 0


def test_chat_without_rag(client: TestClient, auth_headers: dict):
    """Test chat endpoint without RAG."""
    request_data = {
        "query": "Hello, how are you?",
        "use_rag": False,
        "max_tokens": 100
    }

    response = client.post(
        "/chat/",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert len(data["citations"]) == 0  # No RAG, so no citations


def test_chat_with_conversation_history(client: TestClient, auth_headers: dict):
    """Test chat with conversation history."""
    request_data = {
        "query": "What about efficiency?",
        "conversation_history": [
            {
                "role": "user",
                "content": "Tell me about solar panels"
            },
            {
                "role": "assistant",
                "content": "Solar panels convert sunlight to electricity..."
            }
        ],
        "use_rag": True
    }

    response = client.post(
        "/chat/",
        json=request_data,
        headers=auth_headers
    )

    assert response.status_code == 200


def test_chat_requires_auth(client: TestClient, sample_chat_request: dict):
    """Test chat endpoint requires authentication."""
    response = client.post(
        "/chat/",
        json=sample_chat_request
    )

    assert response.status_code == 403


def test_chat_stream_not_implemented(client: TestClient, auth_headers: dict, sample_chat_request: dict):
    """Test streaming endpoint returns not implemented."""
    response = client.post(
        "/chat/stream",
        json=sample_chat_request,
        headers=auth_headers
    )

    assert response.status_code == 501
