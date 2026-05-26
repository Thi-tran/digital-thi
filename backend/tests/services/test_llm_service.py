"""
Tests for app/services/llm_service.py
"""
from unittest.mock import MagicMock, patch

import pytest

from app.models import SearchResult
import app.services.llm_service as svc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section(content: str = "Python developer", similarity: float = 0.9):
    return SearchResult(
        content=content, section_type="skills", similarity=similarity
    )


async def _collect(async_gen) -> list[str]:
    """Drain an async generator into a list."""
    chunks = []
    async for chunk in async_gen:
        chunks.append(chunk)
    return chunks


# ---------------------------------------------------------------------------
# stream_chat_response – no sections
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_yields_fallback_when_no_sections():
    chunks = await _collect(svc.stream_chat_response("prompt", []))
    assert len(chunks) == 1
    assert "couldn't find" in chunks[0].lower()


# ---------------------------------------------------------------------------
# stream_chat_response – normal streaming
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_streams_chunks_from_ollama():
    fake_chunks = [
        {"response": "Hello"},
        {"response": " world"},
        {"response": "!"},
    ]
    mock_client = MagicMock()
    mock_client.generate.return_value = iter(fake_chunks)

    with patch.object(svc, "_client", mock_client):
        chunks = await _collect(
            svc.stream_chat_response("some prompt", [_section()])
        )

    assert chunks == ["Hello", " world", "!"]


@pytest.mark.asyncio
async def test_empty_response_chunks_are_skipped():
    """Chunks with empty 'response' strings must not be yielded."""
    fake_chunks = [
        {"response": ""},
        {"response": "data"},
        {"response": ""},
    ]
    mock_client = MagicMock()
    mock_client.generate.return_value = iter(fake_chunks)

    with patch.object(svc, "_client", mock_client):
        chunks = await _collect(
            svc.stream_chat_response("prompt", [_section()])
        )

    assert chunks == ["data"]


@pytest.mark.asyncio
async def test_passes_prompt_and_model_to_client():
    mock_client = MagicMock()
    mock_client.generate.return_value = iter([{"response": "ok"}])

    with patch.object(svc, "_client", mock_client):
        await _collect(svc.stream_chat_response("my prompt", [_section()]))

    mock_client.generate.assert_called_once_with(
        model=svc.CHAT_MODEL,
        prompt="my prompt",
        stream=True,
    )

