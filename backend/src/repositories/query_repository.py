"""
Query repository for database operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import Query
from src.core.exceptions import NotFoundError
from src.core.logging import get_logger

logger = get_logger(__name__)


class QueryRepository:
    """Repository for query CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        query_text: str,
        document_filter: Optional[List[UUID]] = None
    ) -> Query:
        """Create new query record."""
        query = Query(
            query_text=query_text,
            document_filter=document_filter
        )
        self.session.add(query)
        await self.session.flush()
        logger.info("Query created", query_id=str(query.id))
        return query
    
    async def get_by_id(self, query_id: UUID) -> Query:
        """Get query by ID."""
        result = await self.session.execute(
            select(Query).where(Query.id == query_id)
        )
        query = result.scalar_one_or_none()
        if not query:
            raise NotFoundError("Query", str(query_id))
        return query
    
    async def update_results(
        self,
        query_id: UUID,
        answer: str,
        confidence_score: float,
        citations: List[Dict[str, Any]],
        total_time_ms: int,
        iteration_count: int,
        debug_data: Optional[Dict[str, Any]] = None
    ) -> Query:
        """Update query with results."""
        query = await self.get_by_id(query_id)
        query.answer = answer
        query.confidence_score = confidence_score
        query.citations = citations
        query.total_time_ms = total_time_ms
        query.iteration_count = iteration_count
        query.debug_data = debug_data
        
        await self.session.flush()
        logger.info(
            "Query results updated",
            query_id=str(query_id),
            iteration_count=iteration_count,
            total_time_ms=total_time_ms
        )
        return query
    
    async def list_recent(self, limit: int = 50) -> List[Query]:
        """List recent queries."""
        result = await self.session.execute(
            select(Query)
            .order_by(Query.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
