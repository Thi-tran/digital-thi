"""
Database migration runner
"""
import os
import importlib.util
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

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
