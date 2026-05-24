"""
Embedding generation service – wraps Google Vertex AI text-embedding-005 calls.
"""
import logging
import os
from google import genai
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Vertex AI configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "digital-tarmo-497317")
LOCATION = os.getenv("GCP_LOCATION", "europe-west1")
_client = genai.Client(enterprise=True, project=PROJECT_ID, location=LOCATION)

EMBED_MODEL = "text-embedding-005"

def generate_embedding(
    text: str,
    cv_section=None,
    embeddings: list[float] | None = None,
) -> list[float]:
    """
    Generate a single embedding vector for *text* using Google Vertex AI.

    If *embeddings* is provided, this helper will reuse them and optionally
    attach them to *cv_section* to avoid a second request.

    Raises:
        HTTPException(500): if embedding generation fails.
    """
    if embeddings is not None:
        if cv_section is not None:
            cv_section.embedding = embeddings
        return embeddings

    logger.info(f"Generating embedding for text ({len(text)} chars)...")

    try:
        response = _client.models.embed_content(
            model=EMBED_MODEL,
            contents=[text],
        )

        # Response may contain a ContentEmbedding wrapper object
        raw_embedding = None
        if hasattr(response, 'embedding'):
            raw_embedding = response.embedding
        elif hasattr(response, 'embeddings') and response.embeddings:
            raw_embedding = response.embeddings[0]
        else:
            logger.error(f"Unexpected response structure: {response}")
            raise HTTPException(status_code=500, detail="Failed to parse embedding response")

        if hasattr(raw_embedding, 'values'):
            embedding = list(raw_embedding.values)
        elif isinstance(raw_embedding, (list, tuple)):
            embedding = [float(x) for x in raw_embedding]
        else:
            logger.error(f"Unexpected embedding payload: {raw_embedding}")
            raise HTTPException(status_code=500, detail="Failed to parse embedding payload")

        if not embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings")

        if cv_section is not None:
            cv_section.embedding = embedding

        logger.info(f"Embedding generated: {len(embedding)} dimensions")
        return embedding
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Embedding generation failed: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate embeddings")
