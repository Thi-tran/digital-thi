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

def _make_client(embedding: list) -> MagicMock:
    """Return a mock Google Vertex AI client whose embed_content() returns *embedding*."""
    client = MagicMock()
    response = MagicMock()
    response.embedding = embedding
    client.models.embed_content.return_value = response
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
    """The raw *text* is forwarded to the Vertex AI client."""
    vector = [0.5] * 768
    mock_client = _make_client(vector)
    with patch.object(svc, "_client", mock_client):
        svc.generate_embedding("test input")

    mock_client.models.embed_content.assert_called_once_with(
        model=svc.EMBED_MODEL, contents=["test input"]
    )


def test_generate_embedding_raises_on_empty_embedding():
    """An empty embedding vector must raise HTTPException(500)."""
    with patch.object(svc, "_client", _make_client([])):
        with pytest.raises(HTTPException) as exc_info:
            svc.generate_embedding("bad input")

    assert exc_info.value.status_code == 500
    assert "embeddings" in exc_info.value.detail.lower()


def test_generate_embedding_raises_on_client_error():
    """Client errors from Vertex AI are caught and converted to HTTPException(500)."""
    mock_client = MagicMock()
    mock_client.models.embed_content.side_effect = RuntimeError("connection refused")
    with patch.object(svc, "_client", mock_client):
        with pytest.raises(HTTPException) as exc_info:
            svc.generate_embedding("crash")

    assert exc_info.value.status_code == 500
