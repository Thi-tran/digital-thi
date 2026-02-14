from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from datetime import datetime
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://digitalthi:digitalthi_password@localhost:5432/digitalthi_db"
)

# Convert to async URL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class CVSection(Base):
    __tablename__ = "cv_sections"

    id = Column(Integer, primary_key=True, index=True)
    section_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))
    metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    user_embedding = Column(Vector(768))
    created_at = Column(DateTime, default=datetime.utcnow)


async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
