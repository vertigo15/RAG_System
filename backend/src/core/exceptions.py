"""
Custom exception hierarchy for the RAG system.
"""

from typing import Optional, Dict, Any


class RAGException(Exception):
    """Base exception for RAG system."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class DocumentProcessingError(RAGException):
    """Exception raised during document processing."""
    
    def __init__(
        self,
        message: str,
        document_id: str,
        stage: str,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="DOCUMENT_PROCESSING_ERROR",
            details={
                "document_id": document_id,
                "stage": stage,
                **kwargs
            }
        )


class EmbeddingError(RAGException):
    """Exception raised during embedding generation."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            details=kwargs
        )


class RetrievalError(RAGException):
    """Exception raised during retrieval."""
    
    def __init__(self, message: str, query_id: str, **kwargs):
        super().__init__(
            message=message,
            error_code="RETRIEVAL_ERROR",
            details={"query_id": query_id, **kwargs}
        )


class NotFoundError(RAGException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )


class ValidationError(RAGException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        details = kwargs
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ExternalServiceError(RAGException):
    """Exception raised when external service calls fail."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = {"service_name": service_name, **kwargs}
        if status_code:
            details["status_code"] = status_code
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details
        )


class RateLimitExceededError(RAGException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after_seconds": retry_after}
        )


class DatabaseError(RAGException):
    """Exception raised for database operations."""
    
    def __init__(self, message: str, operation: str, **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={"operation": operation, **kwargs}
        )


class QueueError(RAGException):
    """Exception raised for queue operations."""
    
    def __init__(self, message: str, queue_name: str, **kwargs):
        super().__init__(
            message=message,
            error_code="QUEUE_ERROR",
            details={"queue_name": queue_name, **kwargs}
        )
