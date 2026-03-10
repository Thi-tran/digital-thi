import asyncio
import logging
import os
from contextlib import asynccontextmanager
from app.embeddings_service import generate_cv_embeddings
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.migrations_runner import run_migrations
from app.embeddings_service import generate_cv_embeddings
from app.models import ChatRequest
from app.routes import (
    chat_endpoint,
    add_cv_section_endpoint,
    get_cv_sections_endpoint,
    generate_embeddings_endpoint,
    health_check,
    ping_ollama,
    get_users_endpoint
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - ping Ollama in the background so the server starts immediately
    logger.info("🔥 Pinging Ollama in the background to wake from cold start...")
    asyncio.create_task(ping_ollama())
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(title="Digital Tarmo Backend API", lifespan=lifespan)

# Get allowed origins from environment or use defaults
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allow_origins = [frontend_url, "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Digital Tarmo Backend API", "status": "running"}

# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    return await chat_endpoint(request, db)

# CV section endpoints
@app.post("/api/cv-section")
async def add_cv_section(request, db: AsyncSession = Depends(get_db)):
    return await add_cv_section_endpoint(request, db)

@app.get("/api/cv-sections")
async def get_cv_sections(db: AsyncSession = Depends(get_db)):
    return await get_cv_sections_endpoint(db)

@app.get("/api/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    return await get_users_endpoint(db)

@app.post("/api/run-migrations")
async def run_migrations_endpoint():
    return await run_migrations()

@app.post("/api/cv-sections/generate-embeddings")
async def generate_embeddings(db: AsyncSession = Depends(get_db)):
    return await generate_embeddings_endpoint(db)

# Health check endpoint
@app.get("/health")
async def health():
    return health_check()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
