"""
Migration 001: Initial schema - create cv_sections and chat_history tables
"""
from sqlalchemy import text

async def upgrade(connection):
    """Create initial tables"""
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
    
    await connection.execute(text("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            user_embedding vector(768),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    print("✓ Migration 001: Initial schema created")


async def downgrade(connection):
    """Drop tables"""
    await connection.execute(text("DROP TABLE IF EXISTS chat_history CASCADE"))
    await connection.execute(text("DROP TABLE IF EXISTS cv_sections CASCADE"))
    print("✓ Migration 001: Rolled back")
