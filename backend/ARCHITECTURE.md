# Backend Architecture

## Overview
The backend is organized into modular, maintainable components following the separation of concerns principle. All Python application code is located in the `app/` directory.

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 - FastAPI application entry point
│   ├── routes.py               - HTTP endpoint implementations
│   ├── models.py               - Pydantic validation models
│   ├── database.py             - SQLAlchemy ORM models
│   ├── migrations_runner.py    - Database migration system
│   ├── embeddings_service.py   - Vector embedding generation
│   └── migrations/             - Database migration files
│       ├── 001_initial_schema.py
│       ├── 002_add_session_id_to_chat_history.py
│       └── 003_populate_cv_sections.py
├── Dockerfile
├── requirements.txt
└── ARCHITECTURE.md
```

### Core Application
- **`app/main.py`** - FastAPI application entry point
  - Defines app initialization and middleware
  - Configures CORS for frontend communication
  - Sets up lifespan hooks for startup/shutdown
  - Defines HTTP route handlers that delegate to routes module
  - Orchestrates startup sequence: database init → migrations → embeddings generation

### Business Logic & Routes
- **`app/routes.py`** - HTTP endpoint implementations
  - `chat_endpoint()` - Process user messages with semantic search
  - `add_cv_section_endpoint()` - Add new CV sections with embeddings
  - `get_cv_sections_endpoint()` - List all CV sections
  - `generate_embeddings_endpoint()` - Generate embeddings for CV sections
  - `health_check()` - Service health verification

### Data Models
- **`app/models.py`** - Pydantic request/response validation models
  - `ChatRequest` - User message + session ID
  - `ChatResponse` - Bot response + relevant CV sections
  - `SearchResult` - CV section with similarity score
  - `AddCVSectionRequest/Response` - CV section creation
  - `EmbeddingResponse` - Embedding metadata

### Database & ORM
- **`app/database.py`** - SQLAlchemy ORM models and database setup
  - `CVSection` - CV sections table with vector embeddings
  - `ChatHistory` - Chat messages and history tracking
  - `init_db()` - Initialize database and extensions
  - `get_db()` - Dependency injection for database sessions
  - Connection pool management with asyncpg

### Data Management
- **`app/migrations_runner.py`** - Database schema migration system
  - `run_migrations()` - Automatically load and execute .py migration files
  - Tracks applied migrations in `_migrations` table
  - Supports multiple sequential migrations
  - Location: `app/migrations/*.py`

- **`app/embeddings_service.py`** - Vector embedding generation
  - `generate_cv_embeddings()` - Generate embeddings for CV sections without them
  - Uses Ollama's nomic-embed-text model
  - Handles error cases gracefully

### Migration Files
Located in `app/migrations/`:
- **`001_initial_schema.py`** - Create cv_sections and chat_history tables
- **`002_add_session_id_to_chat_history.py`** - Add session tracking with indexing
- **`003_populate_cv_sections.py`** - Seed database with 8 sample CV sections

## Data Flow

### Chat Request Flow
```
User Message (Frontend)
  ↓
/api/chat (main.py route)
  ↓
chat_endpoint() (routes.py)
  ↓
1. Generate embedding for user message (Ollama)
2. Search similar CV sections (pgvector similarity)
3. Fetch chat history for session (PostgreSQL)
4. Generate response (Ollama with context)
5. Store in chat_history (PostgreSQL)
  ↓
Response with relevant sections (Frontend)
```

### Startup Sequence
```
FastAPI App Start
  ↓
lifespan context manager (main.py)
  ↓
1. await init_db() - Setup database and extensions
2. await run_migrations() - Apply pending migrations
3. await generate_cv_embeddings() - Create embeddings for CV sections
  ↓
App Ready for Requests
```

## Key Technologies

- **FastAPI** - High-performance async web framework
- **PostgreSQL** - Relational database with pgvector extension
- **SQLAlchemy** - Async ORM for database operations
- **Ollama** - Local LLM for embeddings and text generation
- **pgvector** - Vector similarity search (768-dimensional embeddings)
- **Pydantic** - Request/response validation and serialization

## Configuration

Environment variables (from `.env`):
```bash
DATABASE_URL=postgresql://digitalthi:digitalthi_password@localhost:5432/digitalthi_db
```

## API Endpoints

### Chat
- `POST /api/chat` - Send message and get response

### CV Sections Management
- `GET /api/cv-sections` - List all CV sections
- `POST /api/cv-section` - Add new CV section
- `POST /api/cv-sections/generate-embeddings` - Generate embeddings

### Health
- `GET /health` - Service health check

## Session Management

- Session IDs generated client-side (UUID format)
- Stored in localStorage on frontend
- Tracked in database for conversation context
- Last 5 messages included for LLM context window

## Vector Database Setup

- Model: `nomic-embed-text` (768 dimensions)
- Vector type: `vector(768)` in PostgreSQL
- Similarity metric: Cosine distance (pgvector default)
- Search formula: `1 - (embedding <=> :embedding)` to convert to similarity score

## Error Handling

- HTTPException for API errors with proper status codes
- Graceful fallbacks when Ollama unavailable
- Logging at INFO level for operations, DEBUG for details
- Error messages include helpful context for troubleshooting
