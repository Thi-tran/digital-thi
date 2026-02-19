"""
Embeddings generation service
"""
import logging
import os
import ollama
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = logging.getLogger(__name__)

# Configure Ollama client with base URL from environment
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ollamaClient = ollama.Client(host=OLLAMA_BASE_URL)


async def generate_cv_embeddings():
    """Generate embeddings for all CV sections that don't have them"""
    try:
        # Create engine and session for this operation
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://digitalthi:digitalthi_password@localhost:5432/digitalthi_db"
        )
        ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        
        engine = create_async_engine(ASYNC_DATABASE_URL)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db_session:
            # Import here to avoid circular dependency
            from app.database import CVSection
            
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
                    response = ollamaClient.embed(
                        model="nomic-embed-text",
                        input=cv_section.content
                    )
                    
                    embedding = response.get("embeddings", [[]])[0]
                    
                    if embedding:
                        cv_section.embedding = embedding
                        db_session.add(cv_section)  # Re-add to session
                        await db_session.commit()
                        await db_session.refresh(cv_section)  # Refresh the object
                        logger.debug(f"✅ Generated embedding for {cv_section.section_type}")
                    else:
                        logger.warning(f"⚠️ Failed to generate embedding for {cv_section.section_type}")
                
                except Exception as e:
                    logger.error(f"❌ Error generating embedding for {cv_section.section_type}: {str(e)}")
                    await db_session.rollback()  # Rollback on error
            
            logger.info("✨ Embedding generation complete")
        
        # Clean up engine
        await engine.dispose()
    
    except Exception as e:
        logger.warning(f"Embedding generation error: {str(e)}")
