"""
Chat services package
"""
from app.services.embedding_service import generate_embedding
from app.services.cv_search_service import search_similar_sections
from app.services.chat_history_service import fetch_recent_history, save_chat_entry, fetch_cached_response
from app.services.prompt_builder import build_chat_prompt
from app.services.llm_service import stream_chat_response
from app.services.reporting_service import (
    get_total_conversations,
    get_active_users,
    get_avg_messages_per_chat,
    get_conversation_trends,
    get_popular_topics,
)

__all__ = [
    "generate_embedding",
    "search_similar_sections",
    "fetch_recent_history",
    "fetch_cached_response",
    "save_chat_entry",
    "build_chat_prompt",
    "stream_chat_response",
    "get_total_conversations",
    "get_active_users",
    "get_avg_messages_per_chat",
    "get_conversation_trends",
    "get_popular_topics",
]
