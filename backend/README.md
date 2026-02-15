# Digital Thi Backend

Python FastAPI backend service that provides embeddings using Ollama's nomic-embed-text model.

## Prerequisites

1. **Python 3.9+** installed
2. **Ollama** installed and running
   ```bash
   # Install Ollama from https://ollama.ai
   # Or on macOS:
   brew install ollama
   ```

3. **Pull the nomic-embed-text model**
   ```bash
   ollama pull nomic-embed-text
   ```

## Setup

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

## Running the Server

```bash
# Make sure Ollama is running
ollama serve

# In another terminal, run the FastAPI server
python main.py
```

The server will start at `http://localhost:3001`

## API Endpoints

### POST /api/chat
Generate embeddings for a text message.

**Request:**
```json
{
  "message": "What is your experience with Python?"
}
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, ...],  // 768-dimensional vector
  "model": "nomic-embed-text",
  "message": "What is your experience with Python?"
}
```

### GET /health
Health check endpoint to verify service status.

### GET /
Root endpoint with API information.

## Development

Run with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 3001
```

## Troubleshooting

**"Model not found" error:**
```bash
ollama pull nomic-embed-text
```

**Ollama connection error:**
- Make sure Ollama is running: `ollama serve`
- Check Ollama status: `ollama list`
