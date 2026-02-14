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

        # Generate embeddings for the user message
        response = ollama.embed(
            model="nomic-embed-text",
            input=request.message
        )

        embedding = response.get("embeddings", [[]])[0]

        if not embedding:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate embeddings"
            )

        logger.info(f"Generated embedding with {len(embedding)} dimensions")

        # Search for similar CV sections using vector similarity
        query = text("""
            SELECT 
                content, 
                section_type, 
                metadata,
                1 - (embedding <=> :embedding::vector) as similarity
            FROM cv_sections
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT 3
        """)
        
        result = await db.execute(query, {"embedding": str(embedding)})
        rows = result.fetchall()

        relevant_sections = [
            SearchResult(
                content=row.content,
                section_type=row.section_type,
                similarity=float(row.similarity),
                metadata=row.metadata
            )
            for row in rows
        ]

        # Generate response based on relevant sections
        if relevant_sections:
            context = "\n".join([f"- {s.content}" for s in relevant_sections])
            response_text = f"Based on my CV, here's what I found:\n{context}"
        else:
            response_text = "I couldn't find specific information about that in my CV. Please ask another question."

        # Store chat history
        chat_entry = ChatHistory(
            user_message=request.message,
            bot_response=response_text,
            user_embedding=embedding
        )
        db.add(chat_entry)
        await db.commit()

        logger.info(f"Found {len(relevant_sections)} relevant sections")

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
