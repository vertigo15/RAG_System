"""
Query API endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schemas import QueryRequest, QueryResponse
from src.services.query_service import QueryService
from src.services.queue_service import QueueService
from src.repositories.query_repository import QueryRepository
from src.dependencies import get_db_session, get_queue_service
from src.core.logging import get_logger

router = APIRouter(prefix="/queries")
logger = get_logger(__name__)


def get_query_service(
    db: AsyncSession = Depends(get_db_session),
    queue_service: QueueService = Depends(get_queue_service)
) -> QueryService:
    """Get query service instance."""
    query_repo = QueryRepository(db)
    return QueryService(query_repo, queue_service)


@router.post("", response_model=QueryResponse)
async def submit_query(
    query_request: QueryRequest,
    service: QueryService = Depends(get_query_service)
):
    """
    Submit a query for processing.
    
    The query will be processed asynchronously by the query worker.
    Poll the GET endpoint to check for results.
    """
    query = await service.submit_query(
        query_text=query_request.query_text,
        document_filter=query_request.document_filter,
        debug_mode=query_request.debug_mode,
        top_k=query_request.top_k or 10,
        rerank_top=query_request.rerank_top or 5
    )
    
    return QueryResponse.model_validate(query)


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(
    query_id: UUID,
    service: QueryService = Depends(get_query_service)
):
    """Get query result by ID."""
    query = await service.get_query(query_id)
    return QueryResponse.model_validate(query)
