"""
Qdrant Client
Vector storage operations for chunks, summaries, and Q&A pairs.
"""

import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient as QdrantClientLib
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

logger = logging.getLogger(__name__)


class QdrantClient:
    """Client for Qdrant vector storage."""
    
    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        vector_size: int = 3072  # text-embedding-3-large dimension
    ):
        self.client = QdrantClientLib(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Ensure collection exists
        self._ensure_collection()
        
        logger.info(f"Qdrant client initialized for collection: {collection_name}")
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.debug(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
            raise
    
    def store_chunks(
        self,
        doc_id: str,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        Store chunk vectors in Qdrant.
        
        Args:
            doc_id: Document UUID
            chunks: List of chunks with embeddings
        
        Returns:
            Number of chunks stored
        """
        logger.info(f"Storing {len(chunks)} chunks for document: {doc_id}")
        
        try:
            points = []
            
            for chunk in chunks:
                # Generate unique ID for this chunk
                chunk_id = str(uuid.uuid4())
                
                # Build payload (metadata)
                payload = {
                    "doc_id": doc_id,
                    "chunk_index": chunk.get("chunk_index"),
                    "text": chunk["text"],
                    "token_count": chunk.get("token_count", 0),
                    "chunk_type": chunk.get("chunk_type", "child"),  # For hierarchical
                    "parent_id": chunk.get("parent_id"),  # For hierarchical
                    "metadata": chunk.get("metadata", {}),
                    "content_type": "chunk"
                }
                
                # Create point
                point = PointStruct(
                    id=chunk_id,
                    vector=chunk["embedding"],
                    payload=payload
                )
                
                points.append(point)
            
            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Stored {len(points)} chunk vectors")
            return len(points)
            
        except Exception as e:
            logger.error(f"Error storing chunks: {e}")
            raise
    
    def store_summary(
        self,
        doc_id: str,
        summary: str,
        summary_embedding: List[float]
    ) -> str:
        """
        Store summary vector in Qdrant.
        
        Args:
            doc_id: Document UUID
            summary: Summary text
            summary_embedding: Summary embedding vector
        
        Returns:
            Summary vector ID
        """
        logger.info(f"Storing summary for document: {doc_id}")
        
        try:
            summary_id = str(uuid.uuid4())
            
            payload = {
                "doc_id": doc_id,
                "text": summary,
                "content_type": "summary"
            }
            
            point = PointStruct(
                id=summary_id,
                vector=summary_embedding,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info("Summary vector stored")
            return summary_id
            
        except Exception as e:
            logger.error(f"Error storing summary: {e}")
            raise
    
    def store_qa_pairs(
        self,
        doc_id: str,
        qa_pairs: List[Dict[str, Any]]
    ) -> int:
        """
        Store Q&A pair vectors in Qdrant.
        
        Args:
            doc_id: Document UUID
            qa_pairs: List of Q&A pairs with embeddings
        
        Returns:
            Number of Q&A vectors stored
        """
        logger.info(f"Storing {len(qa_pairs)} Q&A pairs for document: {doc_id}")
        
        try:
            points = []
            
            for qa in qa_pairs:
                # Store question vector
                question_id = str(uuid.uuid4())
                question_payload = {
                    "doc_id": doc_id,
                    "text": qa.get("question", ""),
                    "answer": qa.get("answer", ""),
                    "qa_type": qa.get("type", "factual"),
                    "content_type": "question"
                }
                
                question_point = PointStruct(
                    id=question_id,
                    vector=qa["question_embedding"],
                    payload=question_payload
                )
                points.append(question_point)
                
                # Store answer vector
                answer_id = str(uuid.uuid4())
                answer_payload = {
                    "doc_id": doc_id,
                    "question": qa.get("question", ""),
                    "text": qa.get("answer", ""),
                    "qa_type": qa.get("type", "factual"),
                    "content_type": "answer"
                }
                
                answer_point = PointStruct(
                    id=answer_id,
                    vector=qa["answer_embedding"],
                    payload=answer_payload
                )
                points.append(answer_point)
            
            # Batch upsert
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Stored {len(points)} Q&A vectors")
            return len(points)
            
        except Exception as e:
            logger.error(f"Error storing Q&A pairs: {e}")
            raise
    
    def delete_document_vectors(self, doc_id: str) -> int:
        """
        Delete all vectors for a document.
        
        Args:
            doc_id: Document UUID
        
        Returns:
            Number of vectors deleted
        """
        logger.info(f"Deleting vectors for document: {doc_id}")
        
        try:
            # Delete by filter
            self.client.delete(
                collection_name=self.collection_name,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "doc_id",
                                "match": {"value": doc_id}
                            }
                        ]
                    }
                }
            )
            
            logger.info(f"Deleted vectors for document: {doc_id}")
            return 0  # Qdrant doesn't return count
            
        except Exception as e:
            logger.error(f"Error deleting document vectors: {e}")
            raise
