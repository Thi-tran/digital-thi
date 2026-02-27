"""
API routes and endpoints
"""
import logging
import os
import asyncio
import httpx
import ollama
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import CVSection
from app.models import (
    ChatRequest, ChatResponse, SearchResult,
    AddCVSectionRequest, AddCVSectionResponse
)
from app.services import (
    generate_embedding,
    search_similar_sections,
    fetch_recent_history,
    save_chat_entry,
    build_chat_prompt,
    stream_chat_response,
)

logger = logging.getLogger(__name__)

# Configure Ollama client with base URL from environment
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ollamaClient = ollama.Client(host=OLLAMA_BASE_URL)


async def chat_endpoint(request: ChatRequest, db: AsyncSession):
    """
    Process a chat message by orchestrating the following steps:
      1. Validate the request.
      2. Generate an embedding for the user message.
      3. Search for relevant CV sections via vector similarity.
      4. Fetch recent conversation history.
      5. Build the LLM prompt.
      6. Stream the LLM response back to the client.
      7. Persist the exchange to the chat history table.
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")

        logger.info(
            f"Processing message for session {request.session_id}: "
            f"{request.message[:50]}..."
        )

        embeddings = generate_embedding(request.message)
        relevant_sections = await search_similar_sections(db, embeddings)
        history_context = await fetch_recent_history(db, request.session_id)
        prompt = build_chat_prompt(request.message, relevant_sections, history_context)
        async def stream_generator():
            response_text = ""
            async for chunk in stream_chat_response(prompt, relevant_sections):
                response_text += chunk
                yield chunk

            await save_chat_entry(
                db,
                session_id=request.session_id,
                user_message=request.message,
                bot_response=response_text,
                user_embedding=embeddings,
            )

        return StreamingResponse(stream_generator(), media_type="text/plain")

    except ollama.ResponseError as e:
        logger.error(f"Ollama error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ollama model error: {str(e)}. Make sure the nomic-embed-text model is installed."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def add_cv_section_endpoint(request: AddCVSectionRequest, db: AsyncSession):
    """
    Add a CV section with embeddings to the database.
    """
    try:
        if not request.content:
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        logger.info(f"Adding CV section: {request.section_type}")

        # Generate embeddings for the CV section content
        response =ollamaClient.embed(
            model="nomic-embed-text",
            input=request.content
        )

        embedding = response.get("embeddings", [[]])[0]

        if not embedding:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate embeddings"
            )

        logger.info(f"Generated embedding with {len(embedding)} dimensions")

        # Create and save CV section
        cv_section = CVSection(
            section_type=request.section_type,
            content=request.content,
            embedding=embedding,
            meta_data=request.metadata
        )
        
        db.add(cv_section)
        await db.commit()
        await db.refresh(cv_section)

        logger.info(f"CV section added with ID: {cv_section.id}")

        return AddCVSectionResponse(
            id=cv_section.id,
            section_type=cv_section.section_type,
            content=cv_section.content,
            embedding_dimensions=len(embedding),
            message="CV section added successfully"
        )

    except ollama.ResponseError as e:
        logger.error(f"Ollama error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ollama model error: {str(e)}. Make sure the nomic-embed-text model is installed."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_cv_sections_endpoint(db: AsyncSession):
    """
    Get all CV sections from the database.
    """
    try:
        result = await db.execute(select(CVSection))
        sections = result.scalars().all()
        
        return {
            "count": len(sections),
            "sections": [
                {
                    "id": s.id,
                    "section_type": s.section_type,
                    "content": s.content,
                    "metadata": s.meta_data,
                    "created_at": s.created_at.isoformat() if s.created_at else None
                }
                for s in sections
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching CV sections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_embeddings_endpoint(db: AsyncSession):
    """
    Generate embeddings for all CV sections that don't have them.
    """
    try:
        # Get all CV sections without embeddings
        result = await db.execute(
            select(CVSection).where(CVSection.embedding == None)
        )
        cv_sections = result.scalars().all()
        
        if not cv_sections:
            return {
                "message": "✨ All CV sections already have embeddings",
                "count": 0
            }
        
        logger.info(f"🔄 Generating embeddings for {len(cv_sections)} CV sections...")
        
        generated_count = 0
        for cv_section in cv_sections:
            try:
                # Generate embedding for the CV section
                response =ollamaClient.embed(
                    model="nomic-embed-text",
                    input=cv_section.content
                )
                
                embedding = response.get("embeddings", [[]])[0]
                
                if embedding:
                    cv_section.embedding = embedding
                    await db.commit()
                    generated_count += 1
                    logger.debug(f"✅ Generated embedding for {cv_section.section_type}")
                else:
                    logger.warning(f"⚠️ Failed to generate embedding for {cv_section.section_type}")
            
            except Exception as e:
                logger.error(f"❌ Error generating embedding for {cv_section.section_type}: {str(e)}")
        
        logger.info(f"✨ Generated {generated_count} embeddings")
        
        return {
            "message": f"✨ Successfully generated embeddings for {generated_count} CV sections",
            "count": generated_count
        }
    
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def health_check():
    """Health check endpoint to verify the service is running."""
    try:
        ollamaClient.list()
        return {"status": "healthy", "ollama": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def ping_ollama():
    """Ping Ollama to wake it from cold start. Retries until reachable."""

    max_retries = 10
    retry_delay = 3  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                if response.status_code == 200:
                    logger.info(f"✅ Ollama is awake (attempt {attempt})")
                    return
        except Exception as e:
            logger.warning(f"⏳ Ollama not ready yet (attempt {attempt}/{max_retries}): {e}")
        await asyncio.sleep(retry_delay)

    logger.error("❌ Ollama did not respond after multiple retries")
