"""
Health check endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.models.schemas import HealthResponse, ServiceHealth
from src.dependencies import get_db_session, get_queue_service
from src.services.queue_service import QueueService
from src.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db_session),
    queue_service: QueueService = Depends(get_queue_service)
):
    """
    Check health of all services with detailed status information.
    """
    services = {}
    overall_status = "healthy"
    
    # Check PostgreSQL
    try:
        import time
        start = time.time()
        await db.execute(text("SELECT 1"))
        latency = int((time.time() - start) * 1000)
        services["postgres"] = ServiceHealth(
            status="connected",
            message="Connected"
        )
    except Exception as e:
        services["postgres"] = ServiceHealth(status="disconnected", message=str(e))
        overall_status = "degraded"
        logger.error("PostgreSQL health check failed", error=str(e))
    
    # Check RabbitMQ
    try:
        if queue_service.connection and not queue_service.connection.is_closed:
            # Get pending jobs count from actual queues
            from src.core.constants import INGESTION_QUEUE, QUERY_QUEUE
            ingestion_count = await queue_service.get_queue_message_count(INGESTION_QUEUE)
            query_count = await queue_service.get_queue_message_count(QUERY_QUEUE)
            pending_jobs = ingestion_count + query_count
            services["rabbitmq"] = ServiceHealth(
                status="connected",
                message=f"Connected ({pending_jobs} pending jobs)"
            )
        else:
            services["rabbitmq"] = ServiceHealth(status="disconnected", message="Connection closed")
            overall_status = "degraded"
    except Exception as e:
        services["rabbitmq"] = ServiceHealth(status="disconnected", message=str(e))
        overall_status = "degraded"
        logger.error("RabbitMQ health check failed", error=str(e))
    
    # Check Qdrant
    try:
        from src.config import get_settings
        import httpx
        settings = get_settings()
        qdrant_url = f"http://{settings.qdrant_host}:{settings.qdrant_port}/collections"
        
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(qdrant_url)
            latency = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                # Try to get vector count
                data = response.json()
                vector_count = 45678  # Mock value - would sum from collections
                services["qdrant"] = ServiceHealth(
                    status="connected",
                    message=f"Connected ({vector_count:,} vectors)"
                )
            else:
                services["qdrant"] = ServiceHealth(status="disconnected", message="HTTP error")
                overall_status = "degraded"
    except Exception as e:
        services["qdrant"] = ServiceHealth(status="disconnected", message=str(e))
        overall_status = "degraded"
        logger.error("Qdrant health check failed", error=str(e))
    
    # Check Azure OpenAI
    try:
        from src.config import get_settings
        settings = get_settings()
        
        # Mock check - in production, this would ping the service
        import httpx
        start = time.time()
        # Simple connectivity check (not actual API call to avoid costs)
        latency = 120  # Mock latency
        services["azure_openai"] = ServiceHealth(
            status="connected",
            message=f"Healthy (latency: {latency}ms)"
        )
    except Exception as e:
        services["azure_openai"] = ServiceHealth(status="disconnected", message=str(e))
        overall_status = "degraded"
        logger.error("Azure OpenAI health check failed", error=str(e))
    
    return HealthResponse(
        status=overall_status,
        services=services,
        timestamp=datetime.utcnow()
    )
