from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, text
import ollama
from typing import List, Optional
import logging
from contextlib import asynccontextmanager
import os
import importlib.util
from pathlib import Path

from database import get_db, init_db, CVSection, ChatHistory, async_sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_migrations():
    """Run all pending database migrations"""
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://digitalthi:digitalthi_password@localhost:5432/digitalthi_db"
    )
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    try:
        engine = create_async_engine(ASYNC_DATABASE_URL)
        
        async with engine.begin() as connection:
            # Create migrations tracking table
            try:
                await connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS _migrations (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            except Exception as e:
                logger.debug(f"Migrations table check: {str(e)}")
            
            # Get applied migrations
            try:
                result = await connection.execute(text("SELECT name FROM _migrations ORDER BY applied_at"))
                rows = result.fetchall()
                applied = [row[0] for row in rows] if rows else []
            except:
                applied = []
            
            # Get migration files
            migrations_dir = Path(__file__).parent / "migrations"
            migration_files = sorted([f for f in migrations_dir.glob("*.py") if f.name != "__init__.py"])
            
            if migration_files:
                logger.info("🔄 Running database migrations...")
                
                for migration_file in migration_files:
                    module_name = migration_file.stem
                    
                    if module_name in applied:
                        logger.info(f"⏭️  {module_name}: Already applied")
                        continue
                    
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, migration_file)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        await module.upgrade(connection)
                        await connection.execute(text(
                            "INSERT INTO _migrations (name) VALUES (:name)"
                        ), {"name": module_name})
                        
                        logger.info(f"✅ {module_name}: Applied")
                    except Exception as e:
                        logger.error(f"❌ {module_name}: Failed - {str(e)}")
            
            logger.info("✨ Migrations complete")
        
        await engine.dispose()
    except Exception as e:
        logger.warning(f"Migration runner error: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Running database migrations...")
    await run_migrations()
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
    session_id: str


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
        
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")

        logger.info(f"Processing message for session {request.session_id}: {request.message[:50]}...")
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
                
                The user asked: "{request.message}"

                Here's the relevant information from the CV:
                {context}

                Please provide a helpful, professional, and engaging response that answers their question based on this information. 
                Remember the context of previous messages if relevant.
                Add a touch of personality and professionalism to make the response feel natural and friendly.
                Keep the response concise but informative.
                
                Make the format of the response clear and easy to read. Use bullet points if listing information, and keep paragraphs short.
                Don't always start the answer with "Okay" or "Sure", just provide the answer directly. Avoid generic phrases and focus on providing specific information from the CV that addresses the user's question.
                """

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


@app.post("/api/cv-sections/generate-embeddings")
async def generate_cv_embeddings_endpoint(db: AsyncSession = Depends(get_db)):
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
                response = ollama.embed(
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
