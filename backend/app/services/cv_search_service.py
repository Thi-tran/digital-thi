"""
CV section similarity-search service.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.models import SearchResult

logger = logging.getLogger(__name__)

_SIMILARITY_QUERY = text("""
    SELECT
        content,
        section_type,
        metadata,
        1 - (embedding <=> CAST(:embeddings AS vector)) AS similarity
    FROM cv_sections
    WHERE embedding IS NOT NULL
    ORDER BY similarity DESC
    LIMIT :limit
""")


async def search_similar_sections(
    db: AsyncSession,
    embeddings: list[float],
    limit: int = 10,
) -> list[SearchResult]:
    """
    Return the *limit* CV sections most similar to *embeddings*.
    """
    logger.info("Executing similarity search...")

    result = await db.execute(
        _SIMILARITY_QUERY,
        {"embeddings": str(embeddings), "limit": limit},
    )
    rows = result.fetchall()

    logger.info(f"Similarity search returned {len(rows)} rows")

    sections = [
        SearchResult(
            content=row.content,
            section_type=row.section_type,
            similarity=float(row.similarity),
            metadata=row.metadata,
        )
        for row in rows
    ]

    if sections:
        top = sections[0]
        logger.debug(
            f"Top match: [{top.section_type}] similarity={top.similarity:.4f} "
            f"– {top.content[:60]}..."
        )

    return sections
