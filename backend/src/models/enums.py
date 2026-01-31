"""
Enums for database models.
"""

from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentDecision(str, Enum):
    """Agent decision types."""
    PROCEED = "proceed"
    REFINE_QUERY = "refine_query"
    EXPAND_SEARCH = "expand_search"
