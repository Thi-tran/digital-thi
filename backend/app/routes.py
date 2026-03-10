"""
API routes and endpoints
"""
import logging
import os
import asyncio
import random
import httpx
import ollama
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import CVSection, ChatHistory
from app.models import (
    ChatRequest, ChatResponse, SearchResult,
    AddCVSectionRequest, AddCVSectionResponse
)
from app.services import (
    generate_embedding,
    search_similar_sections,
    fetch_recent_history,
    fetch_cached_response,
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

        # Fetch history first – used both as a cache gate and later for the prompt
        history_context = await fetch_recent_history(db, request.session_id)

        # Only check cache for the very first message in a session.
        # By the time the user sends a second message, Ollama is already warm
        # and cached responses would carry the wrong context anyway.
        if not history_context:
            cached_response = await fetch_cached_response(db, request.message)
            if cached_response:
                logger.info(f"Cache hit for session {request.session_id} – replaying cached response")

                async def cached_stream_generator():
                    await asyncio.sleep(random.uniform(1.0, 2.0))
                    words = cached_response.split(" ")
                    for i, word in enumerate(words):
                        chunk = word if i == 0 else " " + word
                        yield chunk
                        await asyncio.sleep(0.03)

                    await save_chat_entry(
                        db,
                        session_id=request.session_id,
                        user_message=request.message,
                        bot_response=cached_response,
                        user_embedding=[],
                    )

                return StreamingResponse(cached_stream_generator(), media_type="text/plain")

        embeddings = generate_embedding(request.message)

        relevant_sections = await search_similar_sections(db, embeddings)
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
    """
    Warm up Ollama by sending a real inference request so the model is
    loaded into memory before the first user message arrives.
    Retries until the request succeeds.
    """
    max_retries = 10
    retry_delay = 3  # seconds

    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                logger.info(f"🔥 Warming up Ollama (attempt {attempt}/{max_retries})...")
                await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={"model": "gemma3", "prompt": "hi", "stream": False},
                )
                logger.info("✅ Ollama model is warm and ready")
                return
        except Exception as e:
            logger.warning(f"⏳ Ollama not ready yet (attempt {attempt}/{max_retries}): {e}")
        await asyncio.sleep(retry_delay)

    logger.error("❌ Ollama did not respond after multiple retries")

async def get_users_endpoint(db: AsyncSession):
    """
    Get all unique users (by session_id) with their conversation counts and activity info.
    Returns a list of users with:
    - session_id
    - conversation_count (number of messages)
    - last_active (most recent message timestamp)
    - joined_date (first message timestamp)
    """
    try:
        # Query to get all distinct sessions with stats
        query = select(
            ChatHistory.session_id,
            func.count(ChatHistory.id).label('conversation_count'),
            func.max(ChatHistory.created_at).label('last_active'),
            func.min(ChatHistory.created_at).label('joined_date')
        ).group_by(ChatHistory.session_id).order_by(func.max(ChatHistory.created_at).desc())
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        users = []
        for row in rows:
            users.append({
                'session_id': row.session_id,
                'conversation_count': row.conversation_count,
                'last_active': row.last_active.isoformat() if row.last_active else None,
                'joined_date': row.joined_date.isoformat() if row.joined_date else None,
            })
        
        return {'users': users}
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

