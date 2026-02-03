"""
Qdrant service for vector operations.
"""

from typing import List, Dict, Any
from uuid import UUID
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from src.core.logging import get_logger
from src.config import get_settings

logger = get_logger(__name__)


class QdrantService:
    """Service for Qdrant vector database operations."""
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncQdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.collection = "documents"  # Default collection name
    
    async def get_document_chunks(self, document_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document from Qdrant.
        
        Args:
            document_id: Document UUID
            
        Returns:
            List of chunks with their data
        """
        try:
            # Scroll through all points for this document
            chunks = []
            offset = None
            
            while True:
                result = await self.client.scroll(
                    collection_name=self.collection,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="document_id",
                                match=MatchValue(value=str(document_id))
                            )
                        ]
                    ),
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False  # Don't need vectors, just metadata
                )
                
                points, next_offset = result
                
                if not points:
                    break
                
                for point in points:
                    chunk_data = {
                        "id": str(point.id),
                        "content": point.payload.get("text", ""),
                        "doc_id": document_id,
                        "type": point.payload.get("type", "text_chunk"),
                        "section": point.payload.get("section", ""),
                        "chunk_index": point.payload.get("chunk_index", 0),
                        "position": point.payload.get("position", 0),
                        "metadata": point.payload.get("metadata", {})
                    }
                    chunks.append(chunk_data)
                
                if next_offset is None:
                    break
                    
                offset = next_offset
            
            # Sort by position
            chunks.sort(key=lambda x: x.get("position", 0))
            
            logger.info(
                "Retrieved chunks from Qdrant",
                document_id=str(document_id),
                chunk_count=len(chunks)
            )
            
            return chunks
            
        except Exception as e:
            logger.exception("Failed to retrieve chunks from Qdrant", document_id=str(document_id))
            return []
    
    async def delete_document_chunks(self, document_id: UUID) -> None:
        """
        Delete all chunks for a document from Qdrant.
        
        Args:
            document_id: Document UUID
        """
        try:
            await self.client.delete(
                collection_name=self.collection,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=str(document_id))
                        )
                    ]
                )
            )
            
            logger.info("Deleted chunks from Qdrant", document_id=str(document_id))
            
        except Exception as e:
            logger.exception("Failed to delete chunks from Qdrant", document_id=str(document_id))
            raise
