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
    Check health of all services.
    """
    services = {}
    overall_status = "healthy"
    
    # Check PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        services["postgres"] = ServiceHealth(status="healthy")
    except Exception as e:
        services["postgres"] = ServiceHealth(status="unhealthy", message=str(e))
        overall_status = "degraded"
        logger.error("PostgreSQL health check failed", error=str(e))
    
    # Check RabbitMQ
    try:
        if queue_service.connection and not queue_service.connection.is_closed:
            services["rabbitmq"] = ServiceHealth(status="healthy")
        else:
            services["rabbitmq"] = ServiceHealth(status="unhealthy", message="Connection closed")
            overall_status = "degraded"
    except Exception as e:
        services["rabbitmq"] = ServiceHealth(status="unhealthy", message=str(e))
        overall_status = "degraded"
        logger.error("RabbitMQ health check failed", error=str(e))
    
    # Qdrant health would be checked by workers
    services["qdrant"] = ServiceHealth(status="unknown", message="Checked by workers")
    
    return HealthResponse(
        status=overall_status,
        services=services,
        timestamp=datetime.utcnow()
    )
