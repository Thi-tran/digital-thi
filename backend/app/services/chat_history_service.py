"""
Chat history service – fetch and persist conversation turns.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import ChatHistory

logger = logging.getLogger(__name__)

_HISTORY_QUERY = text("""
    SELECT *
    FROM chat_history
    WHERE session_id = :session_id
    ORDER BY created_at ASC
""")

_CACHE_TEXT_QUERY = text("""
    SELECT bot_response
    FROM chat_history
    WHERE LOWER(user_message) = LOWER(:user_message)
    ORDER BY created_at ASC
    LIMIT 1
""")


async def fetch_recent_history(
    db: AsyncSession,
    session_id: str,
    turns: int = 5,
) -> str:
    """
    Return the last *turns* conversation turns for *session_id* as a
    formatted string ready to be embedded in an LLM prompt.
    """
    result = await db.execute(_HISTORY_QUERY, {"session_id": session_id})
    rows = result.fetchall()

    if not rows:
        return ""

    lines: list[str] = []
    for msg in rows[-turns:]:
        lines.append(f"User: {msg.user_message}")
        lines.append(f"Assistant: {msg.bot_response}")

    logger.debug(f"Loaded {len(rows[-turns:])} history turns for session {session_id}")
    return "\n".join(lines) + "\n\n"


async def fetch_cached_response(
    db: AsyncSession,
    user_message: str,
) -> str:
    """
    Return the cached bot_response for the most recent entry whose
    user_message matches *user_message* (case-insensitive).

    Returns an empty string on a cache miss.
    """
    result = await db.execute(
        _CACHE_TEXT_QUERY,
        {"user_message": user_message},
    )
    row = result.fetchone()

    if not row:
        logger.debug("Cache miss for message: %s", user_message[:60])
        return ""

    logger.debug("Cache hit for message: %s", user_message[:60])
    return row.bot_response


async def save_chat_entry(
    db: AsyncSession,
    session_id: str,
    user_message: str,
    bot_response: str,
    user_embedding: list[float],
) -> None:
    """
    Persist a single user/bot exchange to the chat_history table.
    Errors are logged but not re-raised so streaming is never interrupted.
    """
    try:
        entry = ChatHistory(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            user_embedding=user_embedding,
        )
        db.add(entry)
        await db.commit()
        logger.debug(f"Chat entry saved for session {session_id}")
    except Exception as exc:
        logger.error(f"Failed to save chat history for session {session_id}: {exc}")
