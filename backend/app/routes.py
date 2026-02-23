"""
API routes and endpoints
"""
import logging
import os
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import ollama

from app.database import CVSection, ChatHistory
from app.models import (
    ChatRequest, ChatResponse, SearchResult,
    AddCVSectionRequest, AddCVSectionResponse
)

logger = logging.getLogger(__name__)

# Configure Ollama client with base URL from environment
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ollamaClient = ollama.Client(host=OLLAMA_BASE_URL)


async def chat_endpoint(request: ChatRequest, db: AsyncSession):
    """
    Process chat message: generate embeddings, search similar CV sections, and return response.
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")

        logger.info(f"Processing message for session {request.session_id}: {request.message[:50]}...")
        print(f"Received message: {request.message[:50]}... {request.session_id}")
        
        # Generate embeddings for the user message
        response = ollamaClient.embed(
            model="nomic-embed-text",
            input=request.message
        )

        embeddings = response.get("embeddings", [[]])[0]
        print(f"Generated embedding: {embeddings[:5]}... (total {len(embeddings)} dimensions)")
        
        if not embeddings:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate embeddings"
            )

        logger.info(f"Generated embedding with {len(embeddings)} dimensions")

        # Search for similar CV sections using vector similarity
        query = text("""
            SELECT 
                content, 
                section_type, 
                metadata,
                1 - (embedding <=> CAST(:embeddings AS vector)) as similarity
            FROM cv_sections
            WHERE embedding IS NOT NULL
            ORDER BY similarity DESC
            LIMIT 10
        """)
        
        logger.info(f"Executing similarity search...")
        result = await db.execute(query, {"embeddings": str(embeddings)})
        rows = result.fetchall()
        logger.info(f"Query returned {len(rows)} rows")
        print(f"Found {len(rows)} similar sections")
        
        relevant_sections = [
            SearchResult(
                content=row.content,
                section_type=row.section_type,
                similarity=float(row.similarity),
                metadata=row.metadata
            )
            for row in rows
        ]
        print(f"Top relevant section: {relevant_sections[0].content[:50]}... with similarity {relevant_sections[0].similarity:.4f}" if relevant_sections else "No relevant sections found")
        
        # Fetch previous chat history for this session
        chat_history_query = text("""
            SELECT 
                *
            FROM chat_history
            WHERE session_id = :session_id
            ORDER BY created_at ASC
        """)

        result = await db.execute(chat_history_query, {"session_id": request.session_id})
        chat_history = result.fetchall()

        # Build conversation context from history
        history_context = ""
        if chat_history:
            history_lines = []
            for msg in chat_history[-5:]:  # Include last 5 messages for context
                history_lines.append(f"User: {msg.user_message}")
                history_lines.append(f"Assistant: {msg.bot_response}")
            history_context = "\n".join(history_lines) + "\n\n" if history_lines else ""
        
        # Generate response based on relevant sections using Ollama
        if relevant_sections:
            # Build context from relevant sections
            context = "\n".join([f"- {s.content}" for s in relevant_sections])
            
            # Create a prompt for Ollama to generate a personalized response
            prompt = f"""You are helping to answer questions about my CV. 
                Previous conversation:
                {history_context}
                
                The user asked: {request.message}

                Here's the relevant information from the CV:
                {context}

                Please provide a helpful, professional, and engaging response that answers their question based on this information. 
                Remember the context of previous messages if relevant.
                Add a touch of personality and professionalism to make the response feel natural and friendly.               
                Make the format of the response clear and easy to read. Use bullet points if listing information, and keep paragraphs short.
                Don't always start the answer with "Okay" or "Sure", just provide the answer directly. Avoid generic phrases and focus on providing specific information from the CV that addresses the user's question.
                Keep the answer short, under 500 characters, and make it engaging. If the question is about a specific skill or experience, highlight that information clearly in the response. If the question is more general, provide a summary of relevant CV sections that could help answer it.
                Be honest in the answer, if the job requirement is not met, acknowledge it and suggest related skills or experiences that could be relevant.
                At the end of the message, try to ask more questions to understand the job description from the recruiter. For example, what kinds of responsibilities or skills are most important for this role? The goal is to understand their needs to fit with my experience too.
                """

            logger.info(f"Generating response with Ollama...")
            try:
                ollama_response = ollamaClient.generate(
                    model="gemma3",
                    prompt=prompt,
                    stream=False
                )
                response_text = ollama_response.get("response", "").strip()
                print(f"Generated response: {response_text[:50]}...")
                
                if not response_text:
                    logger.warning(f"Failed to generate response with Ollama")
                    response_text = f"Based on my CV, here's what I found:\n{context}"
            except Exception as e:
                logger.warning(f"Failed to generate response with Ollama: {str(e)}")
                response_text = f"Based on my CV, here's what I found:\n{context}"
        else:
            response_text = "I couldn't find specific information about that in my CV. Feel free to ask me about my skills, experience, education, or projects!"

        # Store chat history with session_id
        chat_entry = ChatHistory(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=response_text,
            user_embedding=embeddings
        )
        db.add(chat_entry)
        await db.commit()

        return ChatResponse(
            response=response_text,
            relevant_sections=relevant_sections
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
