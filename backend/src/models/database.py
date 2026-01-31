"""
SQLAlchemy database models.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ARRAY, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Document(Base):
    """Document model."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(255), nullable=False)
    file_size_bytes = Column(BigInteger)
    mime_type = Column(String(100))
    status = Column(String(50), default="pending", nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    processing_started_at = Column(TIMESTAMP(timezone=True))
    processing_completed_at = Column(TIMESTAMP(timezone=True))
    processing_time_seconds = Column(Float)
    chunk_count = Column(Integer, default=0)
    vector_count = Column(Integer, default=0)
    qa_pairs_count = Column(Integer, default=0)
    detected_languages = Column(ARRAY(Text))
    summary = Column(Text)
    tags = Column(ARRAY(Text))
    error_message = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Query(Base):
    """Query model."""
    __tablename__ = "queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    query_text = Column(Text, nullable=False)
    answer = Column(Text)
    confidence_score = Column(Float)
    citations = Column(JSONB)
    total_time_ms = Column(Integer)
    iteration_count = Column(Integer)
    debug_data = Column(JSONB)
    document_filter = Column(ARRAY(UUID(as_uuid=True)))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)


class Setting(Base):
    """Settings key-value store."""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class RateLimit(Base):
    """Rate limit tracking."""
    __tablename__ = "rate_limits"
    
    key = Column(String(255), primary_key=True)
    window_start = Column(TIMESTAMP(timezone=True), primary_key=True)
    request_count = Column(Integer, default=1)


class Database:
    """Database connection manager."""
    
    def __init__(self, url: str):
        """Initialize database connection."""
        self.engine = create_async_engine(url, echo=False, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
    
    def get_session(self) -> AsyncSession:
        """Get database session."""
        return self.session_factory()
