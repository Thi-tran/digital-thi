"""
LLM service – streams a response from Google Vertex AI (Gemini).
"""
import logging
import os
from typing import AsyncGenerator

from google import genai
from google.genai import types

from app.models import SearchResult

logger = logging.getLogger(__name__)

# Vertex AI configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "digital-tarmo-497317")
LOCATION = os.getenv("GCP_LOCATION", "europe-west1")
_client = genai.Client(enterprise=True, project=PROJECT_ID, location=LOCATION)

CHAT_MODEL = "gemini-2.5-flash" 

_FALLBACK_NO_SECTIONS = (
    "I couldn't find specific information about that in my CV. "
    "Feel free to ask me about my skills, experience, education, or projects!"
)


async def stream_chat_response(
    prompt: str,
    relevant_sections: list[SearchResult],
) -> AsyncGenerator[str, None]:
    """
    Yield response chunks from the Vertex AI Gemini model.

    * If *relevant_sections* is empty the function yields a single fallback
      string and returns immediately.
    * If Vertex AI raises an error the function falls back to a plain-text summary
      of the sections.
    """
    if not relevant_sections:
        yield _FALLBACK_NO_SECTIONS
        return

    logger.info("Streaming response from Vertex AI Gemini...")
    print(f"Prompt: {prompt}")
    try:
        response = _client.models.generate_content_stream(
            model=CHAT_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )

        for chunk in response:
            if hasattr(chunk, 'text') and chunk.text:
                yield chunk.text
                # Yield control so the event-loop can flush the chunk
                import asyncio
                await asyncio.sleep(0)

    except Exception as exc:
        logger.warning(f"Vertex AI generation failed, using fallback: {exc}")
        fallback = "Based on my CV, here's what I found:\n" + "\n".join(
            f"- {s.content}" for s in relevant_sections
        )
        yield fallback
