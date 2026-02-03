"""
Document service with business logic.
"""

import os
import shutil
from typing import List, Optional
from uuid import UUID
from pathlib import Path
from fastapi import UploadFile
from src.repositories.document_repository import DocumentRepository
from src.services.queue_service import QueueService
from src.services.qdrant_service import QdrantService
from src.models.database import Document
from src.models.enums import DocumentStatus
from src.core.logging import get_logger
from src.core.exceptions import ValidationError
from src.core.constants import MAX_FILE_SIZE_MB, ALLOWED_MIME_TYPES

logger = get_logger(__name__)


class DocumentService:
    """Service for document operations."""
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        queue_service: QueueService,
        upload_dir: str = "/app/uploads"
    ):
        self.document_repo = document_repo
        self.queue_service = queue_service
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_document(self, file: UploadFile) -> Document:
        """
        Upload and process document.
        
        Args:
            file: Uploaded file
            
        Returns:
            Document record
        """
        # Validate file
        self._validate_file(file)
        
        # Create document record
        document = await self.document_repo.create(
            filename=file.filename,
            file_size_bytes=file.size,
            mime_type=file.content_type
        )
        
        # Save file
        file_path = self.upload_dir / f"{document.id}_{file.filename}"
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            logger.info(
                "File saved",
                document_id=str(document.id),
                filename=file.filename,
                file_path=str(file_path)
            )
            
            # Publish ingestion job
            await self.queue_service.publish_ingestion_job(
                document_id=str(document.id),
                file_path=str(file_path)
            )
            
            return document
            
        except Exception as e:
            # Cleanup on failure
            if file_path.exists():
                file_path.unlink()
            await self.document_repo.update_status(
                document.id,
                DocumentStatus.FAILED,
                error_message=str(e)
            )
            raise
    
    async def get_document(self, document_id: UUID) -> Document:
        """Get document by ID."""
        return await self.document_repo.get_by_id(document_id)
    
    async def list_documents(
        self,
        status: Optional[DocumentStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Document], int]:
        """List documents with pagination."""
        return await self.document_repo.list_all(status, limit, offset)
    
    async def delete_document(self, document_id: UUID) -> None:
        """
        Delete document and associated files.
        
        Args:
            document_id: Document ID
        """
        document = await self.document_repo.get_by_id(document_id)
        
        # Delete chunks from Qdrant
        try:
            qdrant_service = QdrantService()
            await qdrant_service.delete_document_chunks(document_id)
        except Exception as e:
            logger.warning("Failed to delete chunks from Qdrant", error=str(e))
        
        # Delete file
        file_pattern = f"{document_id}_*"
        for file_path in self.upload_dir.glob(file_pattern):
            file_path.unlink()
            logger.info("File deleted", file_path=str(file_path))
        
        # Delete database record
        await self.document_repo.delete(document_id)
        
        logger.info("Document deleted", document_id=str(document_id))
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        if not file.filename:
            raise ValidationError("Filename is required")
        
        if file.size and file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(
                f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB",
                field="file"
            )
        
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"File type {file.content_type} is not allowed",
                field="file",
                allowed_types=ALLOWED_MIME_TYPES
            )
