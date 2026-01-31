"""
Request/response logging middleware.
"""

import time
from uuid import uuid4
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import get_logger, request_id_var, correlation_id_var

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs all HTTP requests and responses with timing."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log details."""
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID', str(uuid4())[:8])
        correlation_id = request.headers.get('X-Correlation-ID', request_id)
        
        # Set context variables for logging
        request_id_var.set(request_id)
        correlation_id_var.set(correlation_id)
        
        start_time = time.perf_counter()
        
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent')
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
            
            # Add custom headers
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Correlation-ID'] = correlation_id
            response.headers['X-Response-Time-Ms'] = str(round(duration_ms, 2))
            
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                "Request failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__
            )
            raise
