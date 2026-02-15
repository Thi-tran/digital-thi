"""
Embeddings generation service
"""
import logging
import ollama
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import CVSection, async_sessionmaker

logger = logging.getLogger(__name__)


async def generate_cv_embeddings():
    """Generate embeddings for all CV sections that don't have them"""
    try:
        # Create a session from the sessionmaker
        session = async_sessionmaker()
        async with session() as db_session:
            # Get all CV sections without embeddings
            result = await db_session.execute(
                select(CVSection).where(CVSection.embedding == None)
            )
            cv_sections = result.scalars().all()
            
            if not cv_sections:
                logger.info("✨ All CV sections already have embeddings")
                return
            
            logger.info(f"🔄 Generating embeddings for {len(cv_sections)} CV sections...")
            
            for cv_section in cv_sections:
                try:
                    # Generate embedding for the CV section
                    response = ollama.embed(
                        model="nomic-embed-text",
                        input=cv_section.content
                    )
                    
                    embedding = response.get("embeddings", [[]])[0]
                    
                    if embedding:
                        cv_section.embedding = embedding
                        await db_session.commit()
                        logger.debug(f"✅ Generated embedding for {cv_section.section_type}")
                    else:
                        logger.warning(f"⚠️ Failed to generate embedding for {cv_section.section_type}")
                
                except Exception as e:
                    logger.error(f"❌ Error generating embedding for {cv_section.section_type}: {str(e)}")
            
            logger.info("✨ Embedding generation complete")
    
    except Exception as e:
        logger.warning(f"Embedding generation error: {str(e)}")
