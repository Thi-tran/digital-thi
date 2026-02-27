"""
Tests for app/services/cv_search_service.py
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import SearchResult
from app.services.cv_search_service import search_similar_sections


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(content: str, section_type: str, similarity: float, metadata=None):
    """Create a simple namespace that mimics a SQLAlchemy Row."""
    row = MagicMock()
    row.content = content
    row.section_type = section_type
    row.similarity = similarity
    row.metadata = metadata
    return row


def _make_db(rows: list) -> AsyncMock:
    """Return a mock AsyncSession whose execute() returns *rows*."""
    result = MagicMock()
    result.fetchall.return_value = rows
    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)
    return db


# ---------------------------------------------------------------------------
# search_similar_sections
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_returns_empty_list_when_no_rows():
    db = _make_db([])
    result = await search_similar_sections(db, [0.1, 0.2])
    assert result == []


@pytest.mark.asyncio
async def test_maps_rows_to_search_results():
    rows = [
        _make_row("Python developer", "skills", 0.95, {"tag": "python"}),
        _make_row("Led team of 5", "experience", 0.80, None),
    ]
    db = _make_db(rows)

    results = await search_similar_sections(db, [0.1] * 768)

    assert len(results) == 2
    first = results[0]
    assert isinstance(first, SearchResult)
    assert first.content == "Python developer"
    assert first.section_type == "skills"
    assert first.similarity == pytest.approx(0.95)
    assert first.metadata == {"tag": "python"}


@pytest.mark.asyncio
async def test_similarity_cast_to_float():
    """similarity must be a Python float even when the DB returns a Decimal."""
    from decimal import Decimal

    rows = [_make_row("content", "education", Decimal("0.7777"), None)]
    db = _make_db(rows)

    results = await search_similar_sections(db, [0.0] * 768)

    assert isinstance(results[0].similarity, float)
    assert results[0].similarity == pytest.approx(0.7777)


@pytest.mark.asyncio
async def test_passes_embeddings_and_limit_to_db():
    """DB execute is called with the embeddings string and default limit."""
    db = _make_db([])
    embeddings = [0.1, 0.2, 0.3]

    await search_similar_sections(db, embeddings, limit=5)

    db.execute.assert_awaited_once()
    _, kwargs = db.execute.call_args
    params = db.execute.call_args[0][1]
    assert params["embeddings"] == str(embeddings)
    assert params["limit"] == 5


@pytest.mark.asyncio
async def test_default_limit_is_ten():
    db = _make_db([])
    await search_similar_sections(db, [0.0])

    params = db.execute.call_args[0][1]
    assert params["limit"] == 10
