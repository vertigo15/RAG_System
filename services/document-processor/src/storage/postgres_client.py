"""
PostgreSQL Client
Database operations for Document Processor.
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PostgreSQLClient:
    """PostgreSQL client for document metadata operations."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("PostgreSQL connection closed")
    
    def update_document_status(
        self,
        doc_id: str,
        processing_status: str,
        error_message: Optional[str] = None
    ):
        """Update document processing status."""
        try:
            with self.conn.cursor() as cur:
                if error_message:
                    cur.execute(
                        """
                        UPDATE documents
                        SET processing_status = %s,
                            status = 'failed',
                            error_message = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (processing_status, error_message, doc_id)
                    )
                else:
                    cur.execute(
                        """
                        UPDATE documents
                        SET processing_status = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (processing_status, doc_id)
                    )
                self.conn.commit()
                logger.info(f"Updated document {doc_id} status to: {processing_status}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to update document status: {e}")
            raise
    
    def update_document_metadata(
        self,
        doc_id: str,
        minio_path: str,
        metadata: Dict[str, Any]
    ):
        """
        Update document with processing metadata.
        
        Args:
            doc_id: Document UUID
            minio_path: MinIO storage path
            metadata: Complete metadata dictionary
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE documents
                    SET
                        processing_status = 'processed',
                        status = 'processing',
                        minio_path = %s,
                        size_category = %s,
                        token_count = %s,
                        token_count_method = %s,
                        primary_language = %s,
                        is_multilingual = %s,
                        summary_method = %s,
                        qa_method = %s,
                        chunking_strategy = %s,
                        qa_pairs_count = %s,
                        processing_completed_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        minio_path,
                        metadata["document"]["size_category"],
                        metadata["document"]["token_count"],
                        metadata["document"]["token_count_method"],
                        metadata["language"]["primary"],
                        metadata["language"]["is_multilingual"],
                        metadata["enrichment"]["summary_method"],
                        metadata["enrichment"]["qa_method"],
                        metadata["chunking"]["recommended_strategy"],
                        metadata["enrichment"]["qa_pairs_count"],
                        doc_id
                    )
                )
                self.conn.commit()
                logger.info(f"Updated document {doc_id} metadata")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to update document metadata: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM documents WHERE id = %s",
                    (doc_id,)
                )
                result = cur.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise
