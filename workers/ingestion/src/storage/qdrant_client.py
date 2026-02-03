import logging
import uuid
from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)

class QdrantStorage:
    """Store document chunks in Qdrant vector database"""
    
    def __init__(self, host: str, port: int, collection: str):
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection = collection
        self.dimension = 3072
    
    async def ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection not in collection_names:
                logger.info(f"Creating collection: {self.collection}")
                await self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    )
                )
            else:
                logger.info(f"Collection {self.collection} already exists")
        
        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")
            raise
    
    async def store_chunks(self, document_id: str, chunks: List[Dict[str, Any]]) -> int:
        """
        Store document chunks in Qdrant
        
        Args:
            document_id: Document UUID
            chunks: List of chunks with embeddings
        
        Returns:
            Number of chunks stored
        """
        logger.info(f"Storing {len(chunks)} chunks for document {document_id}")
        
        await self.ensure_collection()
        
        points = []
        for idx, chunk in enumerate(chunks):
            embedding = chunk.get("embedding")
            if not embedding:
                logger.warning(f"Chunk {idx} has no embedding, skipping")
                continue
            
            # Generate a valid UUID for the point ID
            point_id = str(uuid.uuid4())
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_id": chunk.get("chunk_id"),
                    "chunk_index": idx,
                    "text": chunk.get("text", ""),
                    "type": chunk.get("type", "text_chunk"),
                    "section": chunk.get("section", ""),
                    "position": chunk.get("position", 0),
                    "language": chunk.get("language", "unknown"),
                    "is_multilingual": chunk.get("is_multilingual", False),
                    "languages": chunk.get("languages", []),
                    "language_distribution": chunk.get("language_distribution", {}),
                    "metadata": chunk.get("metadata", {})
                }
            )
            points.append(point)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            await self.client.upsert(
                collection_name=self.collection,
                points=batch
            )
        
        logger.info(f"Stored {len(points)} points in Qdrant")
        return len(points)
    
    async def delete_document_chunks(self, document_id: str):
        """Delete all chunks for a document"""
        try:
            await self.client.delete(
                collection_name=self.collection,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "document_id",
                                "match": {"value": document_id}
                            }
                        ]
                    }
                }
            )
            logger.info(f"Deleted chunks for document {document_id}")
        
        except Exception as e:
            logger.error(f"Failed to delete chunks: {e}")
