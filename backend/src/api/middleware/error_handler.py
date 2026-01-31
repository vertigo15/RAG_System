"""
Global error handler middleware.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.exceptions import RAGException, NotFoundError
from src.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler with consistent JSON responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Handle all errors consistently."""
        try:
            return await call_next(request)
            
        except NotFoundError as e:
            logger.info(
                "Resource not found",
                error_code=e.error_code,
                details=e.details
            )
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=e.to_dict()
            )
            
        except RAGException as e:
            logger.error(
                "Application error",
                error_code=e.error_code,
                details=e.details
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=e.to_dict()
            )
            
        except ValueError as e:
            logger.warning("Validation error", error=str(e))
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "VALIDATION_ERROR",
                    "message": str(e)
                }
            )
            
        except Exception as e:
            logger.exception(
                "Unexpected error",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
