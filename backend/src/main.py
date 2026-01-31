"""
FastAPI main application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.core.logging import setup_logging, get_logger
from src.models.database import Database
from src.services.queue_service import QueueService
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware, PostgresRateLimiter, RateLimitConfig
from src.api.routes import health
import src.dependencies as deps

settings = get_settings()
setup_logging(level=settings.log_level, json_format=settings.log_json)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting RAG System Backend", env=settings.app_env)
    
    # Initialize database
    deps.db_instance = Database(settings.postgres_url)
    logger.info("Database initialized")
    
    # Initialize queue service
    deps.queue_service_instance = QueueService(settings.rabbitmq_url)
    await deps.queue_service_instance.connect()
    logger.info("Queue service connected")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    await deps.queue_service_instance.close()
    await deps.db_instance.close()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Production-ready RAG system with Azure OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware (order matters - applied in reverse)
app.add_middleware(ErrorHandlerMiddleware)

# Rate limiting
rate_limiter = PostgresRateLimiter(
    RateLimitConfig(
        requests_per_minute=settings.rate_limit_per_minute,
        requests_per_hour=settings.rate_limit_per_hour
    )
)
app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=rate_limiter,
    get_db_session=deps.get_db_session
)

app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, tags=["Health"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
