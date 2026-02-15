-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for storing CV information with embeddings
CREATE TABLE IF NOT EXISTS cv_sections (
    id SERIAL PRIMARY KEY,
    section_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS cv_sections_embedding_idx 
ON cv_sections USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create table for chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    user_embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for chat history embeddings
CREATE INDEX IF NOT EXISTS chat_history_embedding_idx 
ON chat_history USING ivfflat (user_embedding vector_cosine_ops)
WITH (lists = 100);
