"""
LLM service – streams a response from the Ollama chat model.
"""
import logging
import os
from typing import AsyncGenerator

import ollama

from app.models import SearchResult

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_client = ollama.Client(host=OLLAMA_BASE_URL)

CHAT_MODEL = "gemma3"

_FALLBACK_NO_SECTIONS = (
    "I couldn't find specific information about that in my CV. "
    "Feel free to ask me about my skills, experience, education, or projects!"
)


async def stream_chat_response(
    prompt: str,
    relevant_sections: list[SearchResult],
) -> AsyncGenerator[str, None]:
    """
    Yield response chunks from the LLM.

    * If *relevant_sections* is empty the function yields a single fallback
      string and returns immediately.
    * If Ollama raises an error the function falls back to a plain-text summary
      of the sections.
    """
    if not relevant_sections:
        yield _FALLBACK_NO_SECTIONS
        return

    logger.info("Streaming response from Ollama...")

    try:
        ollama_response = _client.generate(
            model=CHAT_MODEL,
            prompt=prompt,
            stream=True,
        )

        for chunk in ollama_response:
            chunk_text: str = chunk.get("response", "")
            if chunk_text:
                yield chunk_text
                # Yield control so the event-loop can flush the chunk
                import asyncio
                await asyncio.sleep(0)

    except ollama.ResponseError as exc:
        logger.warning(f"Ollama generation failed, using fallback: {exc}")
        fallback = "Based on my CV, here's what I found:\n" + "\n".join(
            f"- {s.content}" for s in relevant_sections
        )
        yield fallback
