"""
Dependency injection for FastAPI.
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import Database
from src.config import get_settings
from src.services.queue_service import QueueService

# Global instances
db_instance: Database = None
queue_service_instance: QueueService = None


def get_db_instance() -> Database:
    """Get database instance."""
    return db_instance


def get_queue_service() -> QueueService:
    """Get queue service instance."""
    return queue_service_instance


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with db_instance.get_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
