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
