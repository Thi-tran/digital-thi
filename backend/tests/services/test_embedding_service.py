"""
Tests for app/services/embedding_service.py
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

import app.services.embedding_service as svc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_client(embeddings: list) -> MagicMock:
    """Return a mock Ollama client whose .embed() returns *embeddings*."""
    client = MagicMock()
    client.embed.return_value = {"embeddings": [embeddings]}
    return client


# ---------------------------------------------------------------------------
# generate_embedding
# ---------------------------------------------------------------------------


def test_generate_embedding_returns_vector():
    """Happy path: client returns a valid vector."""
    vector = [0.1, 0.2, 0.3]
    with patch.object(svc, "_client", _make_client(vector)):
        result = svc.generate_embedding("hello world")

    assert result == vector


def test_generate_embedding_passes_text_to_client():
    """The raw *text* is forwarded to the Ollama client."""
    vector = [0.5] * 768
    mock_client = _make_client(vector)
    with patch.object(svc, "_client", mock_client):
        svc.generate_embedding("test input")

    mock_client.embed.assert_called_once_with(
        model=svc.EMBED_MODEL, input="test input"
    )


def test_generate_embedding_raises_on_empty_embedding():
    """An empty embedding vector must raise HTTPException(500)."""
    with patch.object(svc, "_client", _make_client([])):
        with pytest.raises(HTTPException) as exc_info:
            svc.generate_embedding("bad input")

    assert exc_info.value.status_code == 500
    assert "embeddings" in exc_info.value.detail.lower()


def test_generate_embedding_raises_on_missing_key():
    """Ollama response without 'embeddings' key must raise HTTPException(500)."""
    mock_client = MagicMock()
    mock_client.embed.return_value = {}  # no "embeddings" key
    with patch.object(svc, "_client", mock_client):
        with pytest.raises(HTTPException) as exc_info:
            svc.generate_embedding("oops")

    assert exc_info.value.status_code == 500


def test_generate_embedding_propagates_ollama_errors():
    """Network / model errors from the client bubble up unchanged."""
    mock_client = MagicMock()
    mock_client.embed.side_effect = RuntimeError("connection refused")
    with patch.object(svc, "_client", mock_client):
        with pytest.raises(RuntimeError, match="connection refused"):
            svc.generate_embedding("crash")
