"""
PostgreSQL-based rate limiting middleware.
"""

import time
from dataclasses import dataclass
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000


class PostgresRateLimiter:
    """Rate limiter using PostgreSQL with sliding window."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
    
    async def check_rate_limit(
        self,
        session: AsyncSession,
        key: str,
        window_seconds: int,
        max_requests: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.
        
        Returns:
            Tuple of (is_allowed, remaining, reset_time_seconds)
        """
        now = time.time()
        window_start = int(now / window_seconds) * window_seconds
        
        # Upsert rate limit record
        result = await session.execute(
            text("""
                INSERT INTO rate_limits (key, window_start, request_count)
                VALUES (:key, to_timestamp(:window_start), 1)
                ON CONFLICT (key, window_start) 
                DO UPDATE SET request_count = rate_limits.request_count + 1
                RETURNING request_count
            """),
            {"key": key, "window_start": window_start}
        )
        
        row = result.fetchone()
        current_count = row[0] if row else 0
        
        remaining = max(0, max_requests - current_count)
        reset_time = int(window_start + window_seconds - now)
        is_allowed = current_count <= max_requests
        
        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                key=key,
                current_count=current_count,
                max_requests=max_requests,
                window_seconds=window_seconds
            )
        
        return is_allowed, remaining, reset_time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces rate limits on API requests."""
    
    EXEMPT_PATHS = {'/health', '/metrics', '/docs', '/openapi.json', '/redoc'}
    
    def __init__(self, app, rate_limiter: PostgresRateLimiter, get_db_session):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.get_db_session = get_db_session
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try API key first
        api_key = request.headers.get('X-API-Key')
        if api_key:
            return f"api_key:{api_key}"
        
        # Fall back to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        client_ip = forwarded.split(',')[0].strip() if forwarded else (
            request.client.host if request.client else 'unknown'
        )
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        
        # Check per-minute limit
        async for session in self.get_db_session():
            is_allowed, remaining, reset_time = await self.rate_limiter.check_rate_limit(
                session=session,
                key=f"{client_key}:minute",
                window_seconds=60,
                max_requests=self.rate_limiter.config.requests_per_minute
            )
            await session.commit()
            break
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after_seconds": reset_time
                },
                headers={
                    "Retry-After": str(reset_time),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Limit": str(self.rate_limiter.config.requests_per_minute)
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers['X-RateLimit-Limit'] = str(self.rate_limiter.config.requests_per_minute)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        
        return response
