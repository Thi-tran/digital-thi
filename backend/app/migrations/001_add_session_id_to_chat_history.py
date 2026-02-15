"""
Migration 002: Add session_id column to chat_history table
"""
from sqlalchemy import text

async def upgrade(connection):
    """Add session_id column to chat_history"""
    await connection.execute(text("""
        ALTER TABLE chat_history 
        ADD COLUMN IF NOT EXISTS session_id VARCHAR(255)
    """))
    
    # Create index on session_id for faster queries
    await connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_chat_history_session_id 
        ON chat_history(session_id)
    """))
    
    # Set default value for existing rows (if any)
    await connection.execute(text("""
        UPDATE chat_history 
        SET session_id = 'default-session' 
        WHERE session_id IS NULL
    """))
    
    # Make session_id NOT NULL after setting defaults
    await connection.execute(text("""
        ALTER TABLE chat_history 
        ALTER COLUMN session_id SET NOT NULL
    """))
    
    print("✓ Migration 002: Added session_id column to chat_history")


async def downgrade(connection):
    """Remove session_id column"""
    await connection.execute(text("""
        DROP INDEX IF EXISTS idx_chat_history_session_id
    """))
    
    await connection.execute(text("""
        ALTER TABLE chat_history 
        DROP COLUMN IF EXISTS session_id
    """))
    
    print("✓ Migration 002: Rolled back")
