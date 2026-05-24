"""
Embeddings generation service
"""
import logging
import os
from google import genai
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = logging.getLogger(__name__)

# Configure Vertex AI client
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "digital-tarmo-497317")
LOCATION = os.getenv("GCP_LOCATION", "europe-west1")
vertexAIClient = genai.Client(enterprise=True, project=PROJECT_ID, location=LOCATION)


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
                    response = vertexAIClient.models.embed_content(
                        model="text-embedding-005",
                        contents=[cv_section.content]
                    )
                    
                    embedding = response.embedding
                    
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
