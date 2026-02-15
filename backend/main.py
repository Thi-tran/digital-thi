from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import ollama
from typing import List, Optional
import logging
from contextlib import asynccontextmanager

from database import get_db, init_db, CVSection, ChatHistory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(title="Digital Thi Backend API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class EmbeddingResponse(BaseModel):
    embedding: List[float]
    model: str
    message: str


class SearchResult(BaseModel):
    content: str
    section_type: str
    similarity: float
    metadata: Optional[dict] = None


class ChatResponse(BaseModel):
    response: str
    relevant_sections: List[SearchResult]


class AddCVSectionRequest(BaseModel):
    section_type: str
    content: str
    metadata: Optional[dict] = None


class AddCVSectionResponse(BaseModel):
    id: int
    section_type: str
    content: str
    embedding_dimensions: int
    message: str


@app.get("/")
async def root():
    return {"message": "Digital Thi Backend API", "status": "running"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Process chat message: generate embeddings, search similar CV sections, and return response.
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"Processing message: {request.message[:50]}...")
        print(f"Received message: {request.message[:50]}...")
        # Generate embeddings for the user message
        response = ollama.embed(
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
        # Generate response based on relevant sections using Ollama
        if relevant_sections:
            # Build context from relevant sections
            context = "\n".join([f"- {s.content}" for s in relevant_sections])
            
            # Create a prompt for Ollama to generate a personalized response
            prompt = f"""You are me to answer questions about my CV. 
                The user asked: "{request.message}"

                Here's the relevant information from the CV:
                {context}

                Please provide a helpful, professional, and engaging response that answers their question based on this information. 
                Add a touch of personality and professionalism to make the response feel natural and friendly.
                Keep the response concise but informative."""

            logger.info(f"Generating response with Ollama...")
            try:
                ollama_response = ollama.generate(
                    model="gemma3",
                    prompt=prompt,
                    stream=False
                )
                response_text = ollama_response.get("response", "").strip()
                print(f"Generated response: {response_text[:50]}...")  # Print the first 50 characters of the response
                if not response_text:
                    logger.warning(f"Failed to generate response with Ollama: {str(e)}")
                    response_text = f"Based on my CV, here's what I found:\n{context}"
            except Exception as e:
                logger.warning(f"Failed to generate response with Ollama: {str(e)}")
                response_text = f"Based on my CV, here's what I found:\n{context}"
        else:
            response_text = "I couldn't find specific information about that in my CV. Feel free to ask me about my skills, experience, education, or projects!"

        # Store chat history
        chat_entry = ChatHistory(
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

@app.post("/api/cv-section", response_model=AddCVSectionResponse)
async def add_cv_section(request: AddCVSectionRequest, db: AsyncSession = Depends(get_db)):
    """
    Add a CV section with embeddings to the database.
    """
    try:
        if not request.content:
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        logger.info(f"Adding CV section: {request.section_type}")

        # Generate embeddings for the CV section content
        response = ollama.embed(
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


@app.get("/api/cv-sections")
async def get_cv_sections(db: AsyncSession = Depends(get_db)):
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

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    try:
        ollama.list()
        return {"status": "healthy", "ollama": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
