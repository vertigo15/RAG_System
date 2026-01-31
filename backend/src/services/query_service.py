"""
Query service with business logic.
"""

from typing import List, Optional
from uuid import UUID
from src.repositories.query_repository import QueryRepository
from src.services.queue_service import QueueService
from src.models.database import Query
from src.core.logging import get_logger

logger = get_logger(__name__)


class QueryService:
    """Service for query operations."""
    
    def __init__(
        self,
        query_repo: QueryRepository,
        queue_service: QueueService
    ):
        self.query_repo = query_repo
        self.queue_service = queue_service
    
    async def submit_query(
        self,
        query_text: str,
        document_filter: Optional[List[UUID]] = None,
        debug_mode: bool = False,
        top_k: int = 10,
        rerank_top: int = 5
    ) -> Query:
        """
        Submit query for processing.
        
        Args:
            query_text: Query text
            document_filter: Optional document ID filter
            debug_mode: Whether to include debug info
            top_k: Initial retrieval count
            rerank_top: Post-rerank count
            
        Returns:
            Query record
        """
        # Create query record
        query = await self.query_repo.create(
            query_text=query_text,
            document_filter=document_filter
        )
        
        logger.info("Query created", query_id=str(query.id), query_text=query_text[:50])
        
        # Publish query job
        await self.queue_service.publish_query_job(
            query_id=str(query.id),
            query_text=query_text,
            document_filter=[str(d) for d in document_filter] if document_filter else None,
            debug_mode=debug_mode,
            top_k=top_k,
            rerank_top=rerank_top
        )
        
        return query
    
    async def get_query(self, query_id: UUID) -> Query:
        """Get query by ID."""
        return await self.query_repo.get_by_id(query_id)
    
    async def list_recent_queries(self, limit: int = 50) -> List[Query]:
        """List recent queries."""
        return await self.query_repo.list_recent(limit)
