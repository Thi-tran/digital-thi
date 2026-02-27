"""
Tests for app/services/chat_history_service.py
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.chat_history_service import fetch_recent_history, save_chat_entry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_msg(user: str, bot: str) -> MagicMock:
    m = MagicMock()
    m.user_message = user
    m.bot_response = bot
    return m


def _make_db(rows: list) -> AsyncMock:
    result = MagicMock()
    result.fetchall.return_value = rows
    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)
    return db


# ---------------------------------------------------------------------------
# fetch_recent_history
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_returns_empty_string_when_no_history():
    db = _make_db([])
    result = await fetch_recent_history(db, session_id="sess-1")
    assert result == ""


@pytest.mark.asyncio
async def test_fetch_formats_single_turn_correctly():
    rows = [_make_msg("Hello", "Hi there!")]
    db = _make_db(rows)

    result = await fetch_recent_history(db, session_id="sess-1")

    assert "User: Hello" in result
    assert "Assistant: Hi there!" in result
    # Must end with double newline for prompt separation
    assert result.endswith("\n\n")


@pytest.mark.asyncio
async def test_fetch_respects_turns_limit():
    """Only the last N turns are included in the output."""
    rows = [_make_msg(f"q{i}", f"a{i}") for i in range(10)]
    db = _make_db(rows)

    result = await fetch_recent_history(db, session_id="sess-2", turns=3)

    # Last 3 messages are q7/a7, q8/a8, q9/a9
    assert "User: q7" in result
    assert "User: q9" in result
    # Earlier messages should NOT appear
    assert "User: q0" not in result
    assert "User: q5" not in result


@pytest.mark.asyncio
async def test_fetch_passes_session_id_to_db():
    db = _make_db([])
    await fetch_recent_history(db, session_id="my-session")

    params = db.execute.call_args[0][1]
    assert params["session_id"] == "my-session"


# ---------------------------------------------------------------------------
# save_chat_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_adds_entry_and_commits():
    db = AsyncMock()
    db.add = MagicMock()

    with patch("app.services.chat_history_service.ChatHistory") as MockHistory:
        instance = MagicMock()
        MockHistory.return_value = instance

        await save_chat_entry(
            db,
            session_id="sess-3",
            user_message="What skills do you have?",
            bot_response="Python, FastAPI...",
            user_embedding=[0.1, 0.2],
        )

    MockHistory.assert_called_once_with(
        session_id="sess-3",
        user_message="What skills do you have?",
        bot_response="Python, FastAPI...",
        user_embedding=[0.1, 0.2],
    )
    db.add.assert_called_once_with(instance)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_does_not_raise_on_db_error():
    """Errors must be silently logged, never re-raised."""
    db = AsyncMock()
    db.add = MagicMock()
    db.commit.side_effect = Exception("DB unavailable")

    # Should complete without raising
    await save_chat_entry(
        db,
        session_id="sess-err",
        user_message="hello",
        bot_response="hi",
        user_embedding=[],
    )
