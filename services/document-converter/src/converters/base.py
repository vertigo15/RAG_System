"""
Base converter class for all document converters.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

from models import ConversionResult, ImageInfo, TableInfo

logger = logging.getLogger(__name__)


class BaseConverter(ABC):
    """Abstract base class for document converters."""
    
    def __init__(
        self,
        vision_service: Optional[object] = None,
        llm_service: Optional[object] = None
    ):
        """
        Initialize converter.
        
        Args:
            vision_service: VisionService instance for image descriptions
            llm_service: LLMService instance for text tasks
        """
        self.vision_service = vision_service
        self.llm_service = llm_service
    
    @abstractmethod
    def convert(self, file_bytes: bytes, filename: str) -> ConversionResult:
        """
        Convert document to markdown.
        
        Args:
            file_bytes: Document binary data
            filename: Original filename
            
        Returns:
            ConversionResult with markdown and metadata
        """
        pass
    
    @abstractmethod
    def get_file_type(self) -> str:
        """
        Get the file type this converter handles.
        
        Returns:
            File type string (e.g., 'pdf', 'docx')
        """
        pass
    
    def _create_success_result(
        self,
        document_id: str,
        filename: str,
        markdown: str,
        processing_time: float,
        images: list = None,
        tables: list = None
    ) -> ConversionResult:
        """
        Create a successful conversion result.
        
        Args:
            document_id: Document UUID
            filename: Original filename
            markdown: Converted markdown content
            processing_time: Processing time in seconds
            images: List of ImageInfo objects
            tables: List of TableInfo objects
            
        Returns:
            ConversionResult
        """
        return ConversionResult(
            success=True,
            document_id=document_id,
            markdown_path=f"markdown/{document_id}.md",
            original_filename=filename,
            file_type=self.get_file_type(),
            image_count=len(images) if images else 0,
            table_count=len(tables) if tables else 0,
            processing_time_seconds=processing_time,
            images=images or [],
            tables=tables or []
        )
    
    def _create_error_result(
        self,
        document_id: str,
        filename: str,
        error: str,
        processing_time: float
    ) -> ConversionResult:
        """
        Create an error conversion result.
        
        Args:
            document_id: Document UUID
            filename: Original filename
            error: Error message
            processing_time: Processing time in seconds
            
        Returns:
            ConversionResult
        """
        return ConversionResult(
            success=False,
            document_id=document_id,
            original_filename=filename,
            file_type=self.get_file_type(),
            processing_time_seconds=processing_time,
            error=error
        )
