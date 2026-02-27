"""
Chat services package
"""
from app.services.embedding_service import generate_embedding
from app.services.cv_search_service import search_similar_sections
from app.services.chat_history_service import fetch_recent_history, save_chat_entry
from app.services.prompt_builder import build_chat_prompt
from app.services.llm_service import stream_chat_response

__all__ = [
    "generate_embedding",
    "search_similar_sections",
    "fetch_recent_history",
    "save_chat_entry",
    "build_chat_prompt",
    "stream_chat_response",
]
