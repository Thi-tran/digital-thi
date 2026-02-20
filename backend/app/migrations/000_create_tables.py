"""
Migration 000: Create initial tables with pgvector extension
"""
from sqlalchemy import text

async def upgrade(connection):
    """Create initial tables"""
    # Enable pgvector extension
    await connection.execute(text("""
        CREATE EXTENSION IF NOT EXISTS vector
    """))
    
    # Create cv_sections table
    await connection.execute(text("""
        CREATE TABLE IF NOT EXISTS cv_sections (
            id SERIAL PRIMARY KEY,
            section_type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create index for cv_sections embeddings
    await connection.execute(text("""
        CREATE INDEX IF NOT EXISTS cv_sections_embedding_idx 
        ON cv_sections USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """))
    
    # Create chat_history table with session_id
    await connection.execute(text("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            user_embedding vector(768),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create index for session_id
    await connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_chat_history_session_id 
        ON chat_history(session_id)
    """))
    
    # Create index for chat_history embeddings
    await connection.execute(text("""
        CREATE INDEX IF NOT EXISTS chat_history_embedding_idx 
        ON chat_history USING ivfflat (user_embedding vector_cosine_ops)
        WITH (lists = 100)
    """))
    
    print("✓ Migration 000: Created initial tables with pgvector extension")


async def downgrade(connection):
    """Drop tables"""
    await connection.execute(text("""
        DROP INDEX IF EXISTS chat_history_embedding_idx
    """))
    
    await connection.execute(text("""
        DROP INDEX IF EXISTS idx_chat_history_session_id
    """))
    
    await connection.execute(text("""
        DROP TABLE IF EXISTS chat_history
    """))
    
    await connection.execute(text("""
        DROP INDEX IF EXISTS cv_sections_embedding_idx
    """))
    
    await connection.execute(text("""
        DROP TABLE IF EXISTS cv_sections
    """))
    
    print("✓ Migration 000: Rolled back")
