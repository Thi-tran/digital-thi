FROM ollama/ollama:latest

# Download and cache models during build
RUN mkdir -p /root/.ollama && \
  ollama serve > /dev/null 2>&1 & \
  OLLAMA_PID=$! && \
  sleep 30 && \
  ollama pull nomic-embed-text && \
  ollama pull gemma3 && \
  kill $OLLAMA_PID || true