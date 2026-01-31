"""
Document repository for database operations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.database import Document
from src.models.enums import DocumentStatus
from src.core.exceptions import NotFoundError
from src.core.logging import get_logger

logger = get_logger(__name__)


class DocumentRepository:
    """Repository for document CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        filename: str,
        file_size_bytes: int,
        mime_type: str
    ) -> Document:
        """Create new document record."""
        document = Document(
            filename=filename,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            status=DocumentStatus.PENDING
        )
        self.session.add(document)
        await self.session.flush()
        logger.info("Document created", document_id=str(document.id), filename=filename)
        return document
    
    async def get_by_id(self, document_id: UUID) -> Document:
        """Get document by ID."""
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        if not document:
            raise NotFoundError("Document", str(document_id))
        return document
    
    async def list_all(
        self,
        status: Optional[DocumentStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Document], int]:
        """List documents with optional filtering."""
        query = select(Document)
        
        if status:
            query = query.where(Document.status == status)
        
        # Get total count
        count_query = select(func.count()).select_from(Document)
        if status:
            count_query = count_query.where(Document.status == status)
        total = await self.session.scalar(count_query)
        
        # Get paginated results
        query = query.order_by(Document.uploaded_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        documents = result.scalars().all()
        
        return list(documents), total
    
    async def update_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
        error_message: Optional[str] = None
    ) -> Document:
        """Update document status."""
        document = await self.get_by_id(document_id)
        document.status = status
        
        if status == DocumentStatus.PROCESSING and not document.processing_started_at:
            document.processing_started_at = datetime.utcnow()
        elif status in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
            document.processing_completed_at = datetime.utcnow()
            if document.processing_started_at:
                duration = (document.processing_completed_at - document.processing_started_at).total_seconds()
                document.processing_time_seconds = duration
        
        if error_message:
            document.error_message = error_message
        
        await self.session.flush()
        logger.info("Document status updated", document_id=str(document_id), status=status)
        return document
    
    async def update_processing_results(
        self,
        document_id: UUID,
        chunk_count: int,
        vector_count: int,
        qa_pairs_count: int,
        summary: str,
        detected_languages: Optional[List[str]] = None
    ) -> Document:
        """Update document with processing results."""
        document = await self.get_by_id(document_id)
        document.chunk_count = chunk_count
        document.vector_count = vector_count
        document.qa_pairs_count = qa_pairs_count
        document.summary = summary
        document.detected_languages = detected_languages
        
        await self.session.flush()
        logger.info(
            "Document processing results updated",
            document_id=str(document_id),
            chunk_count=chunk_count,
            vector_count=vector_count
        )
        return document
    
    async def delete(self, document_id: UUID) -> None:
        """Delete document."""
        document = await self.get_by_id(document_id)
        await self.session.delete(document)
        await self.session.flush()
        logger.info("Document deleted", document_id=str(document_id))
