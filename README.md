# Digital Me - Full Stack Setup with Docker

This project includes a Next.js frontend, FastAPI backend with Ollama embeddings, and PostgreSQL with pgvector for semantic search.

## Prerequisites

1. **Docker & Docker Compose** installed
2. **Ollama** running on your host machine
   ```bash
   brew install ollama
   ollama serve
   ollama pull nomic-embed-text
   ollama pull gemma3
   ```

## Quick Start

### 1. Start Ollama and pull models

```bash
# Start Ollama on your host machine
ollama serve

### 2. Start backend services with Docker Compose

```bash
# From the project root
docker compose up -d
```

This will start:
- PostgreSQL with pgvector (port 5432)
- FastAPI backend (port 3001)

### 3. Start the frontend (separately)

```bash
cd frontend
pnpm install
pnpm run dev
```

Frontend runs at `http://localhost:3000`

## Services

### PostgreSQL (pgvector)
- **Port**: 5432
- **Database**: digitalthi_db
- **User**: digitalthi
- **Password**: digitalthi_password
- **Extensions**: pgvector for similarity search

### Backend API
- **Port**: 3001
- **Tech**: FastAPI + SQLAlchemy + Ollama
- **Features**: 
  - Vector embeddings using nomic-embed-text
  - Semantic search with pgvector
  - Chat history storage

### Frontend
- **Port**: 3000
- **Tech**: Next.js 15 + TypeScript + Tailwind

## API Endpoints

### POST /api/chat
Main chat endpoint with semantic search:
```bash
curl -X POST http://localhost:3001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your skills?"}'
```

Response:
```json
{
  "response": "Based on my CV...",
  "relevant_sections": [
    {
      "content": "Python, JavaScript, TypeScript...",
      "section_type": "skills",
      "similarity": 0.85,
      "metadata": {"category": "technical"}
    }
  ]
}
```

### GET /health
Check service health:
```bash
curl http://localhost:3001/health
```

### POST /api/embeddings
Generate embeddings only:
```bash
curl -X POST http://localhost:3001/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

## Database Schema

### cv_sections
Stores CV information with vector embeddings:
- `id`: Primary key
- `section_type`: Category (skills, experience, etc.)
- `content`: Text content
- `embedding`: 768-dimensional vector
- `metadata`: JSONB for additional info

### chat_history
Stores conversation history:
- `user_message`: User's question
- `bot_response`: Bot's answer
- `user_embedding`: Vector of user message
- `created_at`: Timestamp

## Development

### Run backend locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make sure PostgreSQL is running via Docker
docker-compose up -d postgres

export DATABASE_URL="postgresql://digitalthi:digitalthi_password@localhost:5432/digitalthi_db"
python main.py
```

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart services

```bash
docker-compose restart backend
```

### Stop all services

```bash
docker-compose down

# Stop and remove volumes (data will be lost)
docker-compose down -v
```

## Troubleshooting

**Backend can't connect to Ollama:**
- Make sure Ollama is running on your host: `ollama serve`
- Docker uses `host.docker.internal` to access host machine

**Database connection errors:**
- Wait for PostgreSQL health check: `docker-compose ps`
- Check logs: `docker-compose logs postgres`

**pgvector not enabled:**
- Rebuild containers: `docker-compose down -v && docker-compose up --build`

**Frontend can't connect to backend:**
- Check `.env.local` in frontend folder
- Should have: `NEXT_PUBLIC_API_URL=http://localhost:3001`

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://digitalthi:digitalthi_password@postgres:5432/digitalthi_db
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:3001
```
