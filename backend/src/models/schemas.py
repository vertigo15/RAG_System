"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from .enums import DocumentStatus


# Document schemas
class DocumentUploadResponse(BaseModel):
    """Response for document upload."""
    id: UUID
    filename: str
    status: DocumentStatus
    message: str


class DocumentResponse(BaseModel):
    """Document response."""
    id: UUID
    filename: str
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    status: DocumentStatus
    uploaded_at: datetime
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    processing_time_seconds: Optional[float]
    chunk_count: int
    vector_count: int
    qa_pairs_count: int
    primary_language: Optional[str] = None  # Primary detected language (e.g., 'en', 'he')
    detected_languages: Optional[List[str]]
    summary: Optional[str]
    tags: Optional[List[str]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """List of documents."""
    documents: List[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    """Chunk response."""
    id: str
    content: str
    doc_id: UUID
    hierarchy_path: Optional[str]
    score: Optional[float]
    metadata: Dict[str, Any]


class ChunksResponse(BaseModel):
    """List of chunks."""
    chunks: List[ChunkResponse]
    total: int


# Query schemas
class QueryRequest(BaseModel):
    """Query request."""
    query_text: str = Field(..., min_length=1, max_length=1000)
    document_filter: Optional[List[UUID]] = None
    debug_mode: bool = False
    top_k: Optional[int] = Field(None, ge=1, le=50)
    rerank_top: Optional[int] = Field(None, ge=1, le=20)


class QueryResponse(BaseModel):
    """Query response."""
    id: UUID
    query_text: str
    answer: Optional[str]
    confidence_score: Optional[float]
    citations: Optional[List[Dict[str, Any]]]
    total_time_ms: Optional[int]
    iteration_count: Optional[int]
    debug_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Settings schemas
class SettingsUpdate(BaseModel):
    """Settings update request."""
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_embedding_deployment: Optional[str] = None
    azure_llm_deployment: Optional[str] = None
    azure_doc_intelligence_endpoint: Optional[str] = None
    azure_doc_intelligence_key: Optional[str] = None
    default_top_k: Optional[int] = Field(None, ge=1, le=100)
    default_rerank_top: Optional[int] = Field(None, ge=1, le=50)
    max_agent_iterations: Optional[int] = Field(None, ge=1, le=10)
    chunk_size: Optional[int] = Field(None, ge=100, le=2000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=500)
    enable_hybrid_search: Optional[bool] = None
    enable_qa_matching: Optional[bool] = None
    
    # Chunking Configuration (new fields)
    semantic_overlap_enabled: Optional[bool] = None
    semantic_overlap_tokens: Optional[int] = Field(None, ge=10, le=200)
    parent_chunk_multiplier: Optional[float] = Field(None, ge=1.5, le=4.0)
    use_llm_for_parent_summary: Optional[bool] = None
    parent_summary_max_length: Optional[int] = Field(None, ge=100, le=500)
    hierarchical_threshold_chars: Optional[int] = Field(None, ge=20000, le=200000)
    semantic_threshold_chars: Optional[int] = Field(None, ge=5000, le=50000)
    min_headers_for_semantic: Optional[int] = Field(None, ge=1, le=10)


class SettingsResponse(BaseModel):
    """Settings response."""
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_embedding_deployment: str
    azure_llm_deployment: str
    azure_doc_intelligence_endpoint: str
    azure_doc_intelligence_key: str
    default_top_k: int
    default_rerank_top: int
    max_agent_iterations: int
    chunk_size: int
    chunk_overlap: int
    enable_hybrid_search: bool = True
    enable_qa_matching: bool = True
    
    # Chunking Configuration (new fields)
    semantic_overlap_enabled: bool = True
    semantic_overlap_tokens: int = 50
    parent_chunk_multiplier: float = 2.0
    use_llm_for_parent_summary: bool = False
    parent_summary_max_length: int = 300
    hierarchical_threshold_chars: int = 60000
    semantic_threshold_chars: int = 12000
    min_headers_for_semantic: int = 3


# Health check schemas
class ServiceHealth(BaseModel):
    """Individual service health."""
    status: str
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Overall health response."""
    status: str
    services: Dict[str, ServiceHealth]
    timestamp: datetime


# Error schemas
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
