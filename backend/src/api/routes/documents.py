"""
Document API endpoints.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.schemas import DocumentUploadResponse, DocumentResponse, DocumentListResponse
from src.models.enums import DocumentStatus
from src.services.document_service import DocumentService
from src.services.queue_service import QueueService
from src.repositories.document_repository import DocumentRepository
from src.dependencies import get_db_session, get_queue_service
from src.core.logging import get_logger

router = APIRouter(prefix="/documents")
logger = get_logger(__name__)


def get_document_service(
    db: AsyncSession = Depends(get_db_session),
    queue_service: QueueService = Depends(get_queue_service)
) -> DocumentService:
    """Get document service instance."""
    document_repo = DocumentRepository(db)
    return DocumentService(document_repo, queue_service)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service)
):
    """
    Upload a document for processing.
    
    Supported formats: PDF, DOCX, PPTX, PNG, JPEG, TXT
    """
    document = await service.upload_document(file)
    
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        message="Document uploaded successfully and queued for processing"
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    status: Optional[DocumentStatus] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: DocumentService = Depends(get_document_service)
):
    """List all documents with optional filtering."""
    documents, total = await service.list_documents(status, limit, offset)
    
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get document by ID."""
    document = await service.get_document(document_id)
    return DocumentResponse.model_validate(document)


@router.get("/{document_id}/chunks", response_model=ChunksResponse)
async def get_document_chunks(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Get all chunks for a document."""
    # This will be implemented with Qdrant integration
    # For now, return empty list
    from src.models.schemas import ChunksResponse
    return ChunksResponse(chunks=[], total=0)


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service)
):
    """Delete document and associated data."""
    await service.delete_document(document_id)
    return {"message": "Document deleted successfully", "document_id": str(document_id)}
