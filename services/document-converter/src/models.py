"""
Pydantic models for Document Converter Service.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ImageInfo(BaseModel):
    """Metadata about an extracted image."""
    image_id: str
    description: str
    page_number: Optional[int] = None
    minio_path: Optional[str] = None


class TableInfo(BaseModel):
    """Metadata about an extracted table."""
    table_id: str
    row_count: int
    column_count: int
    has_summary: bool = False
    sheet_name: Optional[str] = None  # For Excel files


class ConversionResult(BaseModel):
    """Result of document conversion."""
    success: bool
    document_id: str
    markdown_path: Optional[str] = None
    original_filename: str
    file_type: str
    image_count: int = 0
    table_count: int = 0
    processing_time_seconds: float
    error: Optional[str] = None
    images: List[ImageInfo] = Field(default_factory=list)
    tables: List[TableInfo] = Field(default_factory=list)


class IncomingMessage(BaseModel):
    """Message received from RabbitMQ ingestion queue."""
    document_id: str
    file_path: str
    original_filename: str
    mime_type: Optional[str] = None
    correlation_id: Optional[str] = None


class ChunkingMessage(BaseModel):
    """Message sent to chunking queue."""
    doc_id: str
    markdown_path: str
    original_filename: str
    file_type: str
    image_count: int = 0
    table_count: int = 0
