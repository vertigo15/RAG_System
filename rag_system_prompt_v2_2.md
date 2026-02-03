# RAG System - Full Implementation Prompt

## Project Overview

Build a production-ready RAG (Retrieval Augmented Generation) system:

- **Deployment:** On-premise using Docker containers
- **Cloud Services:** Azure OpenAI (embeddings + LLM), Azure Document Intelligence
- **Architecture:** Microservices with RabbitMQ for job management
- **UI:** Full admin interface for document management, querying, and debugging
- **Code Quality:** Clean, debuggable, production-grade code following best practices

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Frontend │  │ Backend  │  │ Ingestion│  │  Query   │       │
│  │  (React) │  │  (API)   │  │  Worker  │  │  Worker  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┼─────────────┼─────────────┘              │
│                     │             │                            │
│              ┌──────┴──────┐  ┌───┴────┐                       │
│              │  RabbitMQ   │  │ Qdrant │                       │
│              └─────────────┘  └────────┘                       │
│                                                                 │
│              ┌─────────────┐                                   │
│              │  PostgreSQL │                                   │
│              └─────────────┘                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────────────┐
              │        Azure Cloud Services           │
              │  ┌───────────┐  ┌────────────────┐   │
              │  │  OpenAI   │  │   Document     │   │
              │  │  Service  │  │  Intelligence  │   │
              │  └───────────┘  └────────────────┘   │
              └───────────────────────────────────────┘
```

---

## Code Quality Standards

### General Principles

1. **Single Responsibility:** Each function/class does one thing well
2. **Dependency Injection:** Pass dependencies, don't hardcode them
3. **Configuration as Code:** All settings via environment variables
4. **Fail Fast:** Validate inputs early, raise clear exceptions
5. **Immutability:** Prefer immutable data structures

### Project Structure

```
project/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── documents.py
│   │   │   │   ├── queries.py
│   │   │   │   ├── settings.py
│   │   │   │   └── health.py
│   │   │   └── middleware/
│   │   │       ├── logging.py
│   │   │       ├── rate_limit.py
│   │   │       └── error_handler.py
│   │   │
│   │   ├── core/
│   │   │   ├── logging.py
│   │   │   ├── exceptions.py
│   │   │   └── constants.py
│   │   │
│   │   ├── models/
│   │   │   ├── database.py
│   │   │   ├── schemas.py
│   │   │   └── enums.py
│   │   │
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   ├── query_service.py
│   │   │   ├── queue_service.py
│   │   │   └── settings_service.py
│   │   │
│   │   └── repositories/
│   │       ├── document_repository.py
│   │       ├── query_repository.py
│   │       └── settings_repository.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       └── integration/
│
├── workers/
│   ├── ingestion/
│   │   ├── Dockerfile
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── consumer.py
│   │   │   ├── pipeline/
│   │   │   │   ├── document_intelligence.py
│   │   │   │   ├── vision_processor.py
│   │   │   │   ├── tree_builder.py
│   │   │   │   ├── chunker.py
│   │   │   │   ├── enrichment.py
│   │   │   │   └── embedder.py
│   │   │   ├── storage/
│   │   │   │   ├── qdrant_client.py
│   │   │   │   └── postgres_client.py
│   │   │   └── core/
│   │   │       ├── logging.py
│   │   │       └── exceptions.py
│   │   └── tests/
│   │
│   └── query/
│       ├── Dockerfile
│       ├── src/
│       │   ├── main.py
│       │   ├── config.py
│       │   ├── consumer.py
│       │   ├── pipeline/
│       │   │   ├── embedder.py
│       │   │   ├── retriever.py
│       │   │   ├── reranker.py
│       │   │   ├── agent.py
│       │   │   └── generator.py
│       │   ├── storage/
│       │   └── core/
│       └── tests/
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   ├── services/
    │   └── types/
    └── tests/
```

---

## Logging System

### JSON Structured Logging

```python
# src/core/logging.py

import logging
import sys
import json
from datetime import datetime
from typing import Any
from contextvars import ContextVar
from uuid import uuid4

request_id_var: ContextVar[str] = ContextVar('request_id', default='')
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": request_id_var.get(''),
            "correlation_id": correlation_id_var.get(''),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        if hasattr(record, 'extra_data'):
            log_data["data"] = record.extra_data
            
        return json.dumps(log_data, default=str)


class ContextLogger:
    """Logger wrapper with automatic context inclusion."""
    
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
    
    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        extra = {'extra_data': kwargs} if kwargs else {}
        self._logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, message, **kwargs)
    
    def exception(self, message: str, **kwargs: Any) -> None:
        self._logger.exception(message, extra={'extra_data': kwargs})


def setup_logging(level: str = "INFO", json_format: bool = True) -> None:
    """Configure application logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        ))
    
    root_logger.addHandler(handler)


def get_logger(name: str) -> ContextLogger:
    """Get a context-aware logger instance."""
    return ContextLogger(name)
```

### Logging Middleware

```python
# src/api/middleware/logging.py

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import get_logger, request_id_var, correlation_id_var
from uuid import uuid4

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all HTTP requests and responses with timing."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get('X-Request-ID', str(uuid4())[:8])
        correlation_id = request.headers.get('X-Correlation-ID', request_id)
        
        request_id_var.set(request_id)
        correlation_id_var.set(correlation_id)
        
        start_time = time.perf_counter()
        
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )
        
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2)
            )
            
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Response-Time-Ms'] = str(round(duration_ms, 2))
            
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "Request failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2)
            )
            raise
```

---

## Rate Limiting

### PostgreSQL-Based Rate Limiter

```python
# src/api/middleware/rate_limit.py

import time
from dataclasses import dataclass
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import get_logger
import asyncpg

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000


class PostgresRateLimiter:
    """Rate limiter using PostgreSQL with sliding window."""
    
    def __init__(self, pool: asyncpg.Pool, config: RateLimitConfig):
        self.pool = pool
        self.config = config
    
    async def initialize(self) -> None:
        """Create rate limiting table."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    key VARCHAR(255) NOT NULL,
                    window_start TIMESTAMP NOT NULL,
                    request_count INTEGER DEFAULT 1,
                    PRIMARY KEY (key, window_start)
                );
                CREATE INDEX IF NOT EXISTS idx_rate_limits_key_time 
                ON rate_limits (key, window_start DESC);
            """)
    
    async def check_rate_limit(
        self, key: str, window_seconds: int, max_requests: int
    ) -> tuple[bool, int, int]:
        """Check if request is within rate limit."""
        now = time.time()
        window_start = int(now / window_seconds) * window_seconds
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO rate_limits (key, window_start, request_count)
                VALUES ($1, to_timestamp($2), 1)
                ON CONFLICT (key, window_start) 
                DO UPDATE SET request_count = rate_limits.request_count + 1
                RETURNING request_count
            """, key, window_start)
            
            current_count = result['request_count']
            remaining = max(0, max_requests - current_count)
            reset_time = int(window_start + window_seconds - now)
            is_allowed = current_count <= max_requests
            
            if not is_allowed:
                logger.warning(
                    "Rate limit exceeded",
                    key=key,
                    current_count=current_count,
                    max_requests=max_requests
                )
            
            return is_allowed, remaining, reset_time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces rate limits on API requests."""
    
    EXEMPT_PATHS = {'/health', '/metrics', '/docs', '/openapi.json'}
    
    def __init__(self, app, rate_limiter: PostgresRateLimiter, config: RateLimitConfig):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.config = config
    
    def _get_client_key(self, request: Request) -> str:
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"api_key:{api_key}"
        
        forwarded = request.headers.get('X-Forwarded-For')
        client_ip = forwarded.split(',')[0].strip() if forwarded else (
            request.client.host if request.client else 'unknown'
        )
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        
        # Check per-minute limit
        is_allowed, remaining, reset_time = await self.rate_limiter.check_rate_limit(
            key=f"{client_key}:minute",
            window_seconds=60,
            max_requests=self.config.requests_per_minute
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": "Rate limit exceeded", "retry_after_seconds": reset_time},
                headers={"Retry-After": str(reset_time), "X-RateLimit-Remaining": "0"}
            )
        
        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(self.config.requests_per_minute)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return response
```

---

## Exception Handling

```python
# src/core/exceptions.py

from typing import Optional, Dict, Any


class RAGException(Exception):
    """Base exception for RAG system."""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.error_code, "message": self.message, "details": self.details}


class DocumentProcessingError(RAGException):
    def __init__(self, message: str, document_id: str, stage: str, **kwargs):
        super().__init__(
            message=message,
            error_code="DOCUMENT_PROCESSING_ERROR",
            details={"document_id": document_id, "stage": stage, **kwargs}
        )


class EmbeddingError(RAGException):
    def __init__(self, message: str, **kwargs):
        super().__init__(message=message, error_code="EMBEDDING_ERROR", details=kwargs)


class RetrievalError(RAGException):
    def __init__(self, message: str, query_id: str, **kwargs):
        super().__init__(
            message=message,
            error_code="RETRIEVAL_ERROR",
            details={"query_id": query_id, **kwargs}
        )


class NotFoundError(RAGException):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )
```

### Error Handler Middleware

```python
# src/api/middleware/error_handler.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.exceptions import RAGException, NotFoundError
from src.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler with consistent JSON responses."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
            
        except NotFoundError as e:
            logger.info("Resource not found", error_code=e.error_code, details=e.details)
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=e.to_dict())
            
        except RAGException as e:
            logger.error("Application error", error_code=e.error_code, details=e.details)
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=e.to_dict())
            
        except Exception as e:
            logger.exception("Unexpected error", error_type=type(e).__name__)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
            )
```

---

## Configuration Management

```python
# src/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "RAG System"
    app_env: str = Field(default="development")
    debug: bool = False
    log_level: str = Field(default="INFO")
    log_json: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # PostgreSQL
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "rag_system"
    postgres_user: str
    postgres_password: str
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    
    # RabbitMQ
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"
    
    # Azure OpenAI
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_embedding_deployment: str = "text-embedding-3-large"
    azure_llm_deployment: str = "gpt-5.3"
    
    # Azure Document Intelligence
    azure_doc_intelligence_endpoint: str
    azure_doc_intelligence_key: str
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # RAG Settings
    default_top_k: int = 10
    default_rerank_top: int = 5
    max_agent_iterations: int = 3
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: rag-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-rag_system}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - rag-network

  qdrant:
    image: qdrant/qdrant:latest
    container_name: rag-qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - rag-network

  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: rag-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER:-guest}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:-guest}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - rag-network

  backend:
    build: ./backend
    container_name: rag-backend
    environment:
      - APP_ENV=${APP_ENV:-development}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - LOG_JSON=true
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=${POSTGRES_DB:-rag_system}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - QDRANT_HOST=qdrant
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_USER=${RABBITMQ_USER:-guest}
      - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-guest}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_DOC_INTELLIGENCE_ENDPOINT=${AZURE_DOC_INTELLIGENCE_ENDPOINT}
      - AZURE_DOC_INTELLIGENCE_KEY=${AZURE_DOC_INTELLIGENCE_KEY}
      - RATE_LIMIT_PER_MINUTE=${RATE_LIMIT_PER_MINUTE:-60}
      - RATE_LIMIT_PER_HOUR=${RATE_LIMIT_PER_HOUR:-1000}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - rag-network

  ingestion-worker:
    build: ./workers/ingestion
    container_name: rag-ingestion-worker
    environment:
      - APP_ENV=${APP_ENV:-development}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - LOG_JSON=true
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=${POSTGRES_DB:-rag_system}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - QDRANT_HOST=qdrant
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_USER=${RABBITMQ_USER:-guest}
      - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-guest}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_DOC_INTELLIGENCE_ENDPOINT=${AZURE_DOC_INTELLIGENCE_ENDPOINT}
      - AZURE_DOC_INTELLIGENCE_KEY=${AZURE_DOC_INTELLIGENCE_KEY}
    volumes:
      - upload_data:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - rag-network

  query-worker:
    build: ./workers/query
    container_name: rag-query-worker
    environment:
      - APP_ENV=${APP_ENV:-development}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - LOG_JSON=true
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=${POSTGRES_DB:-rag_system}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - QDRANT_HOST=qdrant
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_USER=${RABBITMQ_USER:-guest}
      - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-guest}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - rag-network

  frontend:
    build: ./frontend
    container_name: rag-frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - rag-network

volumes:
  postgres_data:
  qdrant_data:
  rabbitmq_data:
  upload_data:

networks:
  rag-network:
    driver: bridge
```

---

## Document Ingestion Pipeline

### Pipeline Flow

```
Upload → RabbitMQ → Worker → Process → Store → Update Status

Worker Steps:
1. Azure Document Intelligence (extract structure)
2. Image Processing (OCR + Vision LLM)
3. Build Unified Document Tree
4. Generate Enrichments (summary + Q&A)
5. Semantic Chunking (language-aware)
6. Generate Embeddings (text-embedding-3-large)
7. Store in Qdrant (chunks, summaries, Q&A)
8. Update PostgreSQL (status, metrics)
```

### Ingestion Worker Example

```python
# workers/ingestion/src/consumer.py

import asyncio
import json
import time
import aio_pika
from src.config import get_settings
from src.core.logging import get_logger, correlation_id_var
from src.pipeline.document_intelligence import DocumentIntelligenceProcessor
from src.pipeline.vision_processor import VisionProcessor
from src.pipeline.tree_builder import TreeBuilder
from src.pipeline.chunker import SemanticChunker
from src.pipeline.enrichment import EnrichmentGenerator
from src.pipeline.embedder import Embedder
from src.storage.qdrant_client import QdrantStorage
from src.storage.postgres_client import PostgresClient

logger = get_logger(__name__)
settings = get_settings()


class IngestionConsumer:
    """RabbitMQ consumer for document ingestion jobs."""
    
    def __init__(self):
        self.doc_intelligence = DocumentIntelligenceProcessor(
            endpoint=settings.azure_doc_intelligence_endpoint,
            api_key=settings.azure_doc_intelligence_key
        )
        self.vision_processor = VisionProcessor(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key
        )
        self.tree_builder = TreeBuilder()
        self.enrichment = EnrichmentGenerator(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            deployment=settings.azure_llm_deployment
        )
        self.chunker = SemanticChunker(
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap
        )
        self.embedder = Embedder(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            deployment=settings.azure_embedding_deployment
        )
        self.qdrant = QdrantStorage(host=settings.qdrant_host, port=settings.qdrant_port)
        self.postgres = PostgresClient(settings.postgres_url)
    
    async def connect(self) -> None:
        logger.info("Connecting to RabbitMQ", host=settings.rabbitmq_host)
        self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        self.queue = await self.channel.declare_queue('ingestion_queue', durable=True)
        logger.info("Connected to RabbitMQ successfully")
    
    async def start_consuming(self) -> None:
        logger.info("Starting to consume messages")
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self._process_message(message)
    
    async def _process_message(self, message: aio_pika.IncomingMessage) -> None:
        try:
            job_data = json.loads(message.body.decode())
            document_id = job_data['document_id']
            file_path = job_data['file_path']
            
            correlation_id_var.set(job_data.get('correlation_id', document_id))
            
            logger.info("Processing ingestion job", document_id=document_id)
            
            await self.postgres.update_document_status(document_id=document_id, status='processing')
            
            result = await self._run_pipeline(document_id, file_path)
            
            await self.postgres.update_document_completed(
                document_id=document_id,
                chunk_count=result['chunk_count'],
                vector_count=result['vector_count'],
                qa_pairs_count=result['qa_pairs_count'],
                summary=result['summary'],
                processing_time=result['processing_time']
            )
            
            logger.info("Ingestion job completed", document_id=document_id, processing_time=result['processing_time'])
            
        except Exception as e:
            logger.exception("Ingestion job failed", document_id=job_data.get('document_id', 'unknown'))
            if 'document_id' in job_data:
                await self.postgres.update_document_status(
                    document_id=job_data['document_id'],
                    status='failed',
                    error_message=str(e)
                )
    
    async def _run_pipeline(self, document_id: str, file_path: str) -> dict:
        start_time = time.perf_counter()
        
        logger.info("Step 1: Document Intelligence", document_id=document_id)
        doc_structure = await self.doc_intelligence.process(document_id, file_path)
        
        logger.info("Step 2: Processing images", document_id=document_id)
        images_processed = await self.vision_processor.process_images(
            document_id=document_id,
            images=doc_structure.get('images', [])
        )
        
        logger.info("Step 3: Building document tree", document_id=document_id)
        document_tree = self.tree_builder.build(structure=doc_structure, image_descriptions=images_processed)
        
        logger.info("Step 4: Generating enrichments", document_id=document_id)
        summary = await self.enrichment.generate_summary(document_tree)
        qa_pairs = await self.enrichment.generate_qa_pairs(document_tree)
        
        logger.info("Step 5: Chunking document", document_id=document_id)
        chunks = self.chunker.chunk(document_tree)
        
        logger.info("Step 6: Generating embeddings", document_id=document_id)
        chunk_embeddings = await self.embedder.embed_chunks(chunks)
        summary_embedding = await self.embedder.embed_text(summary)
        qa_embeddings = await self.embedder.embed_qa_pairs(qa_pairs)
        
        logger.info("Step 7: Storing in Qdrant", document_id=document_id)
        await self.qdrant.store_chunks(document_id, chunk_embeddings)
        await self.qdrant.store_summary(document_id, summary, summary_embedding)
        await self.qdrant.store_qa_pairs(document_id, qa_embeddings)
        
        processing_time = time.perf_counter() - start_time
        
        return {
            'chunk_count': len(chunks),
            'vector_count': len(chunk_embeddings) + 1 + len(qa_embeddings),
            'qa_pairs_count': len(qa_pairs),
            'summary': summary,
            'processing_time': round(processing_time, 2)
        }
```

---

## Query Pipeline (Agentic RAG)

### Pipeline Flow

```
Query → Embed → Hybrid Search → Rerank → Agent Evaluate → Generate/Retry

Agent Decisions:
- PROCEED: Generate answer
- REFINE_QUERY: Modify query and retry
- EXPAND_SEARCH: Broaden search and retry

Max iterations: 3
```

### Agent Evaluator

```python
# workers/query/src/pipeline/agent.py

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from src.core.logging import get_logger

logger = get_logger(__name__)


class AgentDecision(Enum):
    PROCEED = "proceed"
    REFINE_QUERY = "refine_query"
    EXPAND_SEARCH = "expand_search"


@dataclass
class EvaluationResult:
    decision: AgentDecision
    confidence: float
    reasoning: str
    refined_query: Optional[str] = None


@dataclass
class IterationDebugInfo:
    iteration_number: int
    query_used: str
    chunks_before_rerank: List[Dict[str, Any]]
    chunks_after_rerank: List[Dict[str, Any]]
    search_sources: Dict[str, int]
    evaluation: EvaluationResult
    duration_ms: float


class AgentEvaluator:
    """Evaluates context sufficiency and decides next action."""
    
    EVALUATION_PROMPT = """
    Evaluate if the retrieved context is sufficient to answer the question.
    
    Question: {query}
    
    Context:
    {context}
    
    Respond with JSON:
    {{
        "decision": "proceed" | "refine_query" | "expand_search",
        "confidence": 0.0-1.0,
        "reasoning": "Brief explanation",
        "refined_query": "New query if refine_query, otherwise null"
    }}
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def evaluate(self, query: str, context: List[Dict], iteration: int) -> EvaluationResult:
        logger.debug("Evaluating context", query=query[:50], context_count=len(context), iteration=iteration)
        
        context_text = "\n\n".join([
            f"[{i}] (score: {c['score']:.2f}) {c['content'][:300]}..."
            for i, c in enumerate(context[:5], 1)
        ])
        
        prompt = self.EVALUATION_PROMPT.format(query=query, context=context_text)
        response = await self.llm_client.complete(prompt=prompt, temperature=0.1, max_tokens=200)
        
        result = self._parse_response(response)
        logger.info("Agent evaluation complete", decision=result.decision.value, confidence=result.confidence)
        
        return result
    
    def _parse_response(self, response: str) -> EvaluationResult:
        import json
        try:
            data = json.loads(response)
            return EvaluationResult(
                decision=AgentDecision(data['decision']),
                confidence=float(data['confidence']),
                reasoning=data['reasoning'],
                refined_query=data.get('refined_query')
            )
        except Exception:
            logger.warning("Failed to parse agent response, defaulting to proceed")
            return EvaluationResult(
                decision=AgentDecision.PROCEED,
                confidence=0.5,
                reasoning="Parse failed, proceeding with available context"
            )
```

---

## Database Schema

### PostgreSQL

```sql
-- init-db.sql

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_seconds FLOAT,
    chunk_count INTEGER DEFAULT 0,
    vector_count INTEGER DEFAULT 0,
    qa_pairs_count INTEGER DEFAULT 0,
    detected_languages TEXT[],
    summary TEXT,
    tags TEXT[],
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    answer TEXT,
    confidence_score FLOAT,
    citations JSONB,
    total_time_ms INTEGER,
    iteration_count INTEGER,
    debug_data JSONB,
    document_filter UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE rate_limits (
    key VARCHAR(255) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    request_count INTEGER DEFAULT 1,
    PRIMARY KEY (key, window_start)
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX idx_rate_limits_key_time ON rate_limits(key, window_start DESC);
```

---

## Qdrant Hybrid Search

```python
# workers/query/src/storage/qdrant_client.py

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, TextIndexParams, TokenizerType, Filter, FieldCondition, MatchAny
from typing import List, Dict, Any
from src.core.logging import get_logger

logger = get_logger(__name__)
EMBEDDING_SIZE = 3072


class QdrantStorage:
    """Qdrant client with hybrid search support."""
    
    CHUNKS_COLLECTION = "documents_chunks"
    SUMMARIES_COLLECTION = "documents_summaries"
    QA_COLLECTION = "documents_qa"
    
    def __init__(self, host: str, port: int):
        self.client = QdrantClient(host=host, port=port)
    
    async def initialize_collections(self) -> None:
        """Create collections with full-text search enabled."""
        if not self.client.collection_exists(self.CHUNKS_COLLECTION):
            self.client.create_collection(
                collection_name=self.CHUNKS_COLLECTION,
                vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE)
            )
            self.client.create_payload_index(
                collection_name=self.CHUNKS_COLLECTION,
                field_name="content",
                field_schema=TextIndexParams(
                    type="text",
                    tokenizer=TokenizerType.MULTILINGUAL,
                    min_token_len=2,
                    max_token_len=20
                )
            )
            logger.info(f"Created collection: {self.CHUNKS_COLLECTION}")
    
    async def hybrid_search(
        self,
        query_embedding: List[float],
        query_text: str,
        top_k: int = 10,
        document_filter: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Hybrid search combining vector and keyword search with RRF fusion."""
        
        search_filter = None
        if document_filter:
            search_filter = Filter(must=[FieldCondition(key="doc_id", match=MatchAny(any=document_filter))])
        
        # Vector search
        vector_results = self.client.search(
            collection_name=self.CHUNKS_COLLECTION,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=top_k,
            with_payload=True
        )
        
        # Keyword search
        keyword_results = self.client.scroll(
            collection_name=self.CHUNKS_COLLECTION,
            scroll_filter=Filter(must=[FieldCondition(key="content", match={"text": query_text})]),
            limit=top_k,
            with_payload=True
        )[0]
        
        return self._reciprocal_rank_fusion(vector_results, keyword_results, top_k)
    
    def _reciprocal_rank_fusion(self, vector_results, keyword_results, top_k: int, k: int = 60) -> List[Dict]:
        """Combine results using RRF algorithm."""
        scores = {}
        payloads = {}
        
        for rank, hit in enumerate(vector_results):
            scores[hit.id] = scores.get(hit.id, 0) + 1 / (k + rank + 1)
            payloads[hit.id] = {
                "id": hit.id,
                "content": hit.payload.get("content"),
                "doc_id": hit.payload.get("doc_id"),
                "hierarchy_path": hit.payload.get("hierarchy_path"),
                "vector_score": hit.score,
                "metadata": hit.payload
            }
        
        for rank, hit in enumerate(keyword_results):
            scores[hit.id] = scores.get(hit.id, 0) + 1 / (k + rank + 1)
            if hit.id not in payloads:
                payloads[hit.id] = {
                    "id": hit.id,
                    "content": hit.payload.get("content"),
                    "doc_id": hit.payload.get("doc_id"),
                    "hierarchy_path": hit.payload.get("hierarchy_path"),
                    "vector_score": 0,
                    "metadata": hit.payload
                }
        
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return [{"score": score, **payloads[doc_id]} for doc_id, score in sorted_results]
```

---

## Frontend UI Specification

### Technology Stack
- React 18 + TypeScript
- TailwindCSS for styling
- React Query for data fetching and caching
- React Router for navigation
- Zustand for state management
- Lucide React for icons

### Project Structure

```
frontend/
├── src/
│   ├── App.tsx
│   ├── index.tsx
│   ├── api/
│   │   ├── client.ts              # Axios instance with interceptors
│   │   ├── documents.ts           # Document API calls
│   │   ├── queries.ts             # Query API calls
│   │   └── settings.ts            # Settings API calls
│   │
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Tabs.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── StatusIndicator.tsx
│   │   │
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   ├── documents/
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── DocumentDetails.tsx
│   │   │   ├── UploadModal.tsx
│   │   │   ├── ChunksViewer.tsx
│   │   │   └── DocumentFilters.tsx
│   │   │
│   │   ├── query/
│   │   │   ├── QueryInput.tsx
│   │   │   ├── AnswerDisplay.tsx
│   │   │   ├── DebugPanel.tsx
│   │   │   ├── ChunksList.tsx
│   │   │   ├── RerankComparison.tsx
│   │   │   ├── AgentDecision.tsx
│   │   │   └── SearchSources.tsx
│   │   │
│   │   └── settings/
│   │       ├── AzureConfig.tsx
│   │       ├── RAGConfig.tsx
│   │       └── SystemStatus.tsx
│   │
│   ├── pages/
│   │   ├── DocumentsPage.tsx
│   │   ├── QueryPage.tsx
│   │   └── SettingsPage.tsx
│   │
│   ├── hooks/
│   │   ├── useDocuments.ts
│   │   ├── useQuery.ts
│   │   ├── useSettings.ts
│   │   └── useToast.ts
│   │
│   ├── store/
│   │   ├── documentStore.ts
│   │   ├── queryStore.ts
│   │   └── settingsStore.ts
│   │
│   ├── types/
│   │   ├── document.ts
│   │   ├── query.ts
│   │   ├── settings.ts
│   │   └── api.ts
│   │
│   └── utils/
│       ├── formatters.ts
│       ├── validators.ts
│       └── constants.ts
│
├── public/
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

---

### Tab 1: Settings Page

#### Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌──────┐                                                                   │
│  │ LOGO │   RAG System                    [Settings] [Documents] [Query]    │
│  └──────┘                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ⚙️ Settings                                                                │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Azure OpenAI Configuration                                         │   │
│  │  ───────────────────────────────────────────────────────────────── │   │
│  │                                                                     │   │
│  │  Endpoint                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ https://your-resource.openai.azure.com                      │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  API Key                                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ ••••••••••••••••••••••••••••••••                            │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  Embedding Model                    LLM Model                       │   │
│  │  ┌─────────────────────────┐       ┌─────────────────────────┐     │   │
│  │  │ text-embedding-3-large▼│       │ gpt-5.3               ▼│     │   │
│  │  └─────────────────────────┘       └─────────────────────────┘     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Azure Document Intelligence                                        │   │
│  │  ───────────────────────────────────────────────────────────────── │   │
│  │                                                                     │   │
│  │  Endpoint                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ https://your-doc-intel.cognitiveservices.azure.com          │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  API Key                                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ ••••••••••••••••••••••••••••••••                            │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  RAG Configuration                                                  │   │
│  │  ───────────────────────────────────────────────────────────────── │   │
│  │                                                                     │   │
│  │  Top K Results          Rerank Top           Max Iterations         │   │
│  │  ┌──────────┐          ┌──────────┐         ┌──────────┐           │   │
│  │  │    10    │          │    5     │         │    3     │           │   │
│  │  └──────────┘          └──────────┘         └──────────┘           │   │
│  │                                                                     │   │
│  │  Chunk Size             Chunk Overlap                               │   │
│  │  ┌──────────┐          ┌──────────┐                                │   │
│  │  │   512    │          │    50    │                                │   │
│  │  └──────────┘          └──────────┘                                │   │
│  │                                                                     │   │
│  │  ┌───┐ Enable Hybrid Search      ┌───┐ Enable Q&A Matching         │   │
│  │  │ ✓ │                           │ ✓ │                             │   │
│  │  └───┘                           └───┘                             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  System Status                                                      │   │
│  │  ───────────────────────────────────────────────────────────────── │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  🟢 PostgreSQL     Connected                                │   │   │
│  │  │  🟢 Qdrant         Connected (45,678 vectors)               │   │   │
│  │  │  🟢 RabbitMQ       Connected (2 pending jobs)               │   │   │
│  │  │  🟢 Azure OpenAI   Healthy (latency: 120ms)                 │   │   │
│  │  │  🟢 Doc Intel      Healthy                                  │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│                                              ┌─────────────────────────┐   │
│                                              │    💾 Save Settings     │   │
│                                              └─────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Component: SystemStatus.tsx

```typescript
interface ServiceStatus {
  name: string;
  status: 'connected' | 'disconnected' | 'degraded';
  details?: string;
  latency?: number;
}

interface SystemStatusProps {
  services: ServiceStatus[];
  onRefresh: () => void;
}

// Status indicators:
// 🟢 connected - service is healthy
// 🟡 degraded - service is slow or partially available  
// 🔴 disconnected - service is unavailable
```

---

### Tab 2: Documents Page

#### Wireframe - Main View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌──────┐                                                                   │
│  │ LOGO │   RAG System                    [Settings] [Documents] [Query]    │
│  └──────┘                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📄 Documents                                                               │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  ┌──────────────────────┐  ┌────────────┐                                  │
│  │  📤 Upload Documents │  │ 🔄 Refresh │   Total: 156 documents           │
│  └──────────────────────┘  └────────────┘                                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  🔍 Search documents...                     Status: [All      ▼]    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌───┬────────────────────┬────────────┬─────────────┬────────┬───┐│   │
│  │  │ ☐ │ Name               │ Status     │ Uploaded    │ Time   │ ⋮ ││   │
│  │  ├───┼────────────────────┼────────────┼─────────────┼────────┼───┤│   │
│  │  │ ☐ │ 📄 Q3_Report.pdf   │ ✅ Complete│ Jan 15 2024 │ 45.2s  │ ⋮ ││   │
│  │  │   │    financial, q3   │            │ 10:30 AM    │        │   ││   │
│  │  ├───┼────────────────────┼────────────┼─────────────┼────────┼───┤│   │
│  │  │ ☐ │ 📄 Technical_Spec  │ 🔄 Process │ Jan 15 2024 │ --     │ ⋮ ││   │
│  │  │   │    .docx           │ 67%        │ 10:45 AM    │        │   ││   │
│  │  ├───┼────────────────────┼────────────┼─────────────┼────────┼───┤│   │
│  │  │ ☐ │ 📄 HR_Policy.pdf   │ ⏳ Queued  │ Jan 15 2024 │ --     │ ⋮ ││   │
│  │  │   │    hr, policy      │ #3 in queue│ 10:50 AM    │        │   ││   │
│  │  ├───┼────────────────────┼────────────┼─────────────┼────────┼───┤│   │
│  │  │ ☐ │ 📄 Old_Manual.pdf  │ ❌ Failed  │ Jan 14 2024 │ --     │ ⋮ ││   │
│  │  │   │    manual          │ OCR Error  │ 3:20 PM     │        │   ││   │
│  │  └───┴────────────────────┴────────────┴─────────────┴────────┴───┘│   │
│  │                                                                     │   │
│  │  ◀ Previous    Page 1 of 16    Next ▶                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📋 Document Details                                      [X Close] │   │
│  │  ───────────────────────────────────────────────────────────────── │   │
│  │                                                                     │   │
│  │  Q3_Report.pdf                                                      │   │
│  │                                                                     │   │
│  │  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐ │   │
│  │  │ File Size   │ Chunks      │ Vectors     │ Q&A Pairs           │ │   │
│  │  │ 2.3 MB      │ 47          │ 52          │ 15                  │ │   │
│  │  └─────────────┴─────────────┴─────────────┴─────────────────────┘ │   │
│  │                                                                     │   │
│  │  Languages: Hebrew, English                                         │   │
│  │  Tags: financial, quarterly, 2024                                   │   │
│  │                                                                     │   │
│  │  Summary:                                                           │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ This quarterly financial report presents the company's      │   │   │
│  │  │ performance for Q3 2024. Key highlights include 15%         │   │   │
│  │  │ revenue growth, expansion into new markets, and improved    │   │   │
│  │  │ operational efficiency across all departments...            │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │   │
│  │  │  👁 View Chunks │ │ 🔄 Reprocess  │ │ 🗑️ Delete      │          │   │
│  │  └────────────────┘ └────────────────┘ └────────────────┘          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Upload Modal Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  📤 Upload Documents                                      [X]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │                    ┌───────────┐                        │   │
│  │                    │  📄 📄 📄  │                        │   │
│  │                    └───────────┘                        │   │
│  │                                                         │   │
│  │            Drag & drop files here                       │   │
│  │                 or click to browse                      │   │
│  │                                                         │   │
│  │         Supported: PDF, DOCX, PNG, JPG, TIFF           │   │
│  │                  Max size: 50MB per file                │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Selected Files:                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  📄 Q4_Report.pdf           4.2 MB           [Remove]   │   │
│  │  📄 Product_Specs.docx      1.8 MB           [Remove]   │   │
│  │  📄 Diagram.png             856 KB           [Remove]   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Tags (optional):                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [financial] [q4] [+Add tag]                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────────────┐  │
│  │     Cancel      │              │  📤 Upload & Process    │  │
│  └─────────────────┘              └─────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Chunks Viewer Modal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  👁 Chunks Viewer - Q3_Report.pdf                                     [X]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Total Chunks: 47    │    Filter: [All Types ▼]    │    Search: [______]   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Chunk #1                                              [paragraph]  │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  Path: Document > Chapter 1 > Introduction                          │   │
│  │  Language: English    │    Characters: 487                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ This quarterly report presents a comprehensive analysis of  │   │   │
│  │  │ our company's financial performance during Q3 2024. The     │   │   │
│  │  │ period was marked by significant growth in key markets...   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  Chunk #2                                                  [table]  │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  Path: Document > Chapter 1 > Financial Summary                     │   │
│  │  Language: English    │    Characters: 892                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ | Metric      | Q2 2024  | Q3 2024  | Change |              │   │   │
│  │  │ |-------------|----------|----------|--------|              │   │   │
│  │  │ | Revenue     | $12.5M   | $15.2M   | +21.6% |              │   │   │
│  │  │ | Net Profit  | $2.1M    | $2.8M    | +33.3% |              │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  Chunk #3                                      [image_description]  │   │
│  │  ─────────────────────────────────────────────────────────────────  │   │
│  │  Path: Document > Chapter 2 > Market Analysis                       │   │
│  │  Language: English    │    Characters: 312                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Bar chart showing quarterly revenue comparison across       │   │   │
│  │  │ regions. North America leads with 45% share, followed by    │   │   │
│  │  │ Europe at 30% and Asia-Pacific at 25%...                    │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  [Load more chunks...]                                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Tab 3: Query & Debug Page

#### Wireframe - Full View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ┌──────┐                                                                   │
│  │ LOGO │   RAG System                    [Settings] [Documents] [Query]    │
│  └──────┘                                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🔍 Query & Debug                                                           │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Enter your question:                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                                                             │   │   │
│  │  │  What were the revenue numbers for Q3 and how do they      │   │   │
│  │  │  compare to the previous quarter?                          │   │   │
│  │  │                                                             │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────┐                                                           │   │
│  │  │  ✓  │ Enable Debug Mode          Documents: [All Documents ▼]   │   │
│  │  └─────┘                                                           │   │
│  │                                                                     │   │
│  │                                          ┌───────────────────────┐ │   │
│  │                                          │   🔍 Ask Question     │ │   │
│  │                                          └───────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  💬 Answer                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Q3 2024 revenue reached **$15.2 million**, representing a         │   │
│  │  **21.6% increase** compared to Q2 2024 ($12.5 million).          │   │
│  │                                                                     │   │
│  │  Key drivers of this growth include:                               │   │
│  │  • Expansion into the European market (+45% regional growth)       │   │
│  │  • Launch of the Enterprise product tier                           │   │
│  │  • Increased customer retention rate (92% vs 87% in Q2)           │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  📎 Sources:                                                        │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ [1] Q3_Report.pdf, page 3 (Financial Summary)               │   │   │
│  │  │ [2] Q3_Report.pdf, page 12 (Regional Breakdown)             │   │   │
│  │  │ [3] Q3_Report.pdf, page 8 (Customer Metrics)                │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌────────────────┬────────────────┬────────────────┐              │   │
│  │  │ Confidence     │ Response Time  │ Iterations     │              │   │
│  │  │ 94%            │ 1.8s           │ 1              │              │   │
│  │  └────────────────┴────────────────┴────────────────┘              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  🔧 Debug Panel                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌──────────────┐ ┌──────────────┐                                 │   │
│  │  │ Iteration 1  │ │ Iteration 2  │     (if multiple iterations)    │   │
│  │  │   (active)   │ │              │                                 │   │
│  │  └──────────────┘ └──────────────┘                                 │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  Query Used:                                                        │   │
│  │  "What were the revenue numbers for Q3 and how do they compare     │   │
│  │   to the previous quarter?"                                         │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  📊 Search Sources:                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                                                             │   │   │
│  │  │   Vector (chunks)     ████████████████░░░░   8 results     │   │   │
│  │  │   Vector (summaries)  ████░░░░░░░░░░░░░░░░   2 results     │   │   │
│  │  │   Vector (Q&A)        ██████░░░░░░░░░░░░░░   3 results     │   │   │
│  │  │   Keyword (BM25)      ██████████░░░░░░░░░░   5 results     │   │   │
│  │  │   ─────────────────────────────────────────────────────    │   │   │
│  │  │   After merge:        14 unique results                    │   │   │
│  │  │                                                             │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  📋 Retrieved Chunks (Before Rerank):                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ #  │ Score  │ Source                │ Preview               │   │   │
│  │  ├────┼────────┼───────────────────────┼───────────────────────┤   │   │
│  │  │ 1  │ 0.892  │ Q3_Report.pdf, ch.12  │ "Q3 revenue reached   │   │   │
│  │  │    │        │ Financial Summary     │ $15.2 million..."     │   │   │
│  │  ├────┼────────┼───────────────────────┼───────────────────────┤   │   │
│  │  │ 2  │ 0.856  │ Q3_Report.pdf, ch.8   │ "Compared to Q2,      │   │   │
│  │  │    │        │ Quarter Comparison    │ this represents..."   │   │   │
│  │  ├────┼────────┼───────────────────────┼───────────────────────┤   │   │
│  │  │ 3  │ 0.834  │ Q3_Report.pdf, ch.3   │ "The financial        │   │   │
│  │  │    │        │ Introduction          │ summary table..."     │   │   │
│  │  ├────┼────────┼───────────────────────┼───────────────────────┤   │   │
│  │  │ 4  │ 0.798  │ Q2_Report.pdf, ch.5   │ "Q2 revenue was       │   │   │
│  │  │    │        │ Summary               │ $12.5 million..."     │   │   │
│  │  ├────┼────────┼───────────────────────┼───────────────────────┤   │   │
│  │  │ 5  │ 0.756  │ Q3_Report.pdf, ch.15  │ "Regional breakdown   │   │   │
│  │  │    │        │ Regional Analysis     │ shows growth..."      │   │   │
│  │  └────┴────────┴───────────────────────┴───────────────────────┘   │   │
│  │                                                                     │   │
│  │  [Show all 14 chunks ▼]                                             │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  ⭐ After Reranking:                                                │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ #  │ Before │ After  │ Source               │ Change        │   │   │
│  │  ├────┼────────┼────────┼──────────────────────┼───────────────┤   │   │
│  │  │ 1  │ 0.892  │ 0.967  │ Q3_Report, ch.12     │ ↑ +0.075      │   │   │
│  │  │ 2  │ 0.798  │ 0.943  │ Q2_Report, ch.5      │ ↑↑ +0.145     │   │   │
│  │  │ 3  │ 0.834  │ 0.912  │ Q3_Report, ch.3      │ ↑ +0.078      │   │   │
│  │  │ 4  │ 0.856  │ 0.856  │ Q3_Report, ch.8      │ ── 0.000      │   │   │
│  │  │ 5  │ 0.756  │ 0.723  │ Q3_Report, ch.15     │ ↓ -0.033      │   │   │
│  │  └────┴────────┴────────┴──────────────────────┴───────────────┘   │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  🤖 Agent Evaluation:                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │                                                             │   │   │
│  │  │  Decision:    ✅ PROCEED                                    │   │   │
│  │  │  Confidence:  0.94                                          │   │   │
│  │  │                                                             │   │   │
│  │  │  Reasoning:                                                 │   │   │
│  │  │  "The retrieved context contains specific Q3 revenue        │   │   │
│  │  │  figures ($15.2M), Q2 comparison data ($12.5M), and        │   │   │
│  │  │  percentage calculations. This is sufficient to provide    │   │   │
│  │  │  a comprehensive answer to the user's question."           │   │   │
│  │  │                                                             │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  ⏱️ Timing Breakdown:                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Embedding:      120ms  ████░░░░░░░░░░░░░░░░                 │   │   │
│  │  │ Hybrid Search:  340ms  ████████████░░░░░░░░                 │   │   │
│  │  │ Reranking:      280ms  ██████████░░░░░░░░░░                 │   │   │
│  │  │ Agent Eval:     180ms  ██████░░░░░░░░░░░░░░                 │   │   │
│  │  │ Generation:     880ms  ██████████████████████████████       │   │   │
│  │  │ ───────────────────────────────────────────────────────    │   │   │
│  │  │ Total:         1800ms                                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Debug Panel with Multiple Iterations Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔧 Debug Panel                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │   │
│  │  │ Iteration 1  │ │ Iteration 2  │ │ Iteration 3  │                │   │
│  │  │              │ │   (active)   │ │   (final)    │                │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘                │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  Iteration 2 Details:                                               │   │
│  │                                                                     │   │
│  │  Original Query: "What is the company strategy?"                    │   │
│  │  Refined Query:  "What is the company's growth strategy for 2024    │   │
│  │                   including market expansion plans?"                 │   │
│  │                                                                     │   │
│  │  Reason for refinement:                                             │   │
│  │  "Initial query too vague. Adding specificity about timeframe       │   │
│  │   and expansion to retrieve more relevant context."                 │   │
│  │                                                                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │                                                                     │   │
│  │  🤖 Agent Decision History:                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Iter │ Decision      │ Confidence │ Action Taken            │   │   │
│  │  ├──────┼───────────────┼────────────┼─────────────────────────┤   │   │
│  │  │  1   │ REFINE_QUERY  │ 0.45       │ Query too vague         │   │   │
│  │  │  2   │ EXPAND_SEARCH │ 0.62       │ Need more context       │   │   │
│  │  │  3   │ PROCEED       │ 0.89       │ Sufficient context      │   │   │
│  │  └──────┴───────────────┴────────────┴─────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### TypeScript Interfaces

```typescript
// types/document.ts

export interface Document {
  id: string;
  filename: string;
  file_size_bytes: number;
  mime_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  uploaded_at: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  processing_time_seconds?: number;
  chunk_count: number;
  vector_count: number;
  qa_pairs_count: number;
  detected_languages: string[];
  summary?: string;
  tags: string[];
  error_message?: string;
}

export interface Chunk {
  id: string;
  doc_id: string;
  chunk_index: number;
  content: string;
  parent_section: string;
  hierarchy_path: string;
  language: string;
  node_type: 'paragraph' | 'table' | 'image_description' | 'heading';
  page_number?: number;
}

// types/query.ts

export interface QueryRequest {
  query_text: string;
  debug_mode: boolean;
  document_filter?: string[];
  settings?: QuerySettings;
}

export interface QuerySettings {
  top_k?: number;
  rerank_top?: number;
  max_iterations?: number;
}

export interface QueryResponse {
  id: string;
  query_text: string;
  answer: string;
  confidence_score: number;
  citations: Citation[];
  total_time_ms: number;
  iteration_count: number;
  debug_data?: DebugData;
}

export interface Citation {
  document_id: string;
  document_name: string;
  chunk_index: number;
  page_number?: number;
  section: string;
}

export interface DebugData {
  iterations: IterationDebug[];
  timing: TimingBreakdown;
}

export interface IterationDebug {
  iteration_number: number;
  query_used: string;
  search_sources: SearchSources;
  chunks_before_rerank: ChunkResult[];
  chunks_after_rerank: ChunkResult[];
  agent_evaluation: AgentEvaluation;
  duration_ms: number;
}

export interface SearchSources {
  vector_chunks: number;
  vector_summaries: number;
  vector_qa: number;
  keyword_bm25: number;
  after_merge: number;
}

export interface ChunkResult {
  id: string;
  score: number;
  source: string;
  section: string;
  preview: string;
  score_change?: number;
}

export interface AgentEvaluation {
  decision: 'proceed' | 'refine_query' | 'expand_search';
  confidence: number;
  reasoning: string;
  refined_query?: string;
}

export interface TimingBreakdown {
  embedding_ms: number;
  search_ms: number;
  rerank_ms: number;
  agent_ms: number;
  generation_ms: number;
  total_ms: number;
}

// types/settings.ts

export interface Settings {
  azure_openai_endpoint: string;
  azure_openai_api_key: string;
  azure_embedding_model: string;
  azure_llm_model: string;
  azure_doc_intelligence_endpoint: string;
  azure_doc_intelligence_key: string;
  rag_top_k: number;
  rag_rerank_top: number;
  rag_max_iterations: number;
  rag_chunk_size: number;
  rag_chunk_overlap: number;
  rag_enable_hybrid: boolean;
  rag_enable_qa_matching: boolean;
}

export interface SystemStatus {
  services: ServiceStatus[];
}

export interface ServiceStatus {
  name: string;
  status: 'connected' | 'disconnected' | 'degraded';
  details?: string;
  latency_ms?: number;
  vector_count?: number;
  pending_jobs?: number;
}
```

---

### Key React Components

#### QueryInput.tsx
```typescript
interface QueryInputProps {
  onSubmit: (query: string, debugMode: boolean, documentFilter?: string[]) => void;
  isLoading: boolean;
  documents: Document[];
}
```

#### DebugPanel.tsx
```typescript
interface DebugPanelProps {
  debugData: DebugData;
  activeIteration: number;
  onIterationChange: (iteration: number) => void;
}
```

#### ChunksList.tsx
```typescript
interface ChunksListProps {
  chunks: ChunkResult[];
  title: string;
  showScoreChange?: boolean;
  maxVisible?: number;
  onShowAll?: () => void;
}
```

#### RerankComparison.tsx
```typescript
interface RerankComparisonProps {
  before: ChunkResult[];
  after: ChunkResult[];
}
```

#### AgentDecision.tsx
```typescript
interface AgentDecisionProps {
  evaluation: AgentEvaluation;
  iterationHistory?: AgentEvaluation[];
}
```

#### SearchSources.tsx
```typescript
interface SearchSourcesProps {
  sources: SearchSources;
}
// Displays horizontal bar chart of search source contributions
```

#### TimingBreakdown.tsx
```typescript
interface TimingBreakdownProps {
  timing: TimingBreakdown;
}
// Displays horizontal bar chart with timing for each pipeline stage
```

---

## Implementation Order

1. **Phase 1: Infrastructure** - Docker compose, PostgreSQL schema, Qdrant collections, RabbitMQ queues
2. **Phase 2: Backend API** - FastAPI setup, middleware, CRUD endpoints
3. **Phase 3: Ingestion Worker** - Full pipeline implementation
4. **Phase 4: Query Worker** - Hybrid search, reranking, agent loop
5. **Phase 5: Frontend** - All three tabs
6. **Phase 6: Polish** - Error handling, monitoring, performance

---

## Best Practices Checklist

- [ ] All functions have type hints
- [ ] All classes have docstrings
- [ ] Structured JSON logging throughout
- [ ] Request ID tracking across services
- [ ] Correlation ID for distributed tracing
- [ ] Rate limiting on all endpoints
- [ ] Health checks for all services
- [ ] Graceful shutdown handling
- [ ] Retry logic with exponential backoff for Azure calls
- [ ] Circuit breaker for external services
- [ ] Connection pooling for databases
- [ ] Environment-based configuration
- [ ] No hardcoded secrets
