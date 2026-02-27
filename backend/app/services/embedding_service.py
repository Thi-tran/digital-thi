"""
Embedding generation service – wraps Ollama embed calls.
"""
import logging
import os
import ollama
from fastapi import HTTPException

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
_client = ollama.Client(host=OLLAMA_BASE_URL)

EMBED_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> list[float]:
    """
    Generate a single embedding vector for *text* using Ollama.

    Raises:
        HTTPException(500): if Ollama returns an empty embedding.
    """
    logger.info(f"Generating embedding for text ({len(text)} chars)...")

    response = _client.embed(model=EMBED_MODEL, input=text)
    embedding: list[float] = response.get("embeddings", [[]])[0]

    if not embedding:
        raise HTTPException(status_code=500, detail="Failed to generate embeddings")

    logger.info(f"Embedding generated: {len(embedding)} dimensions")
    return embedding
