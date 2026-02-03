"""
PostgreSQL Client
Database operations for Chunking Service.
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional

logger = logging.getLogger(__name__)


class PostgreSQLClient:
    """PostgreSQL client for chunking metadata operations."""
    
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
    
    def update_document_chunking_complete(
        self,
        doc_id: str,
        chunk_count: int,
        vector_count: int
    ):
        """
        Update document with chunking completion.
        
        Args:
            doc_id: Document UUID
            chunk_count: Number of chunks created
            vector_count: Total vectors stored (chunks + summary + QA)
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE documents
                    SET
                        processing_status = 'completed',
                        status = 'completed',
                        chunk_count = %s,
                        vector_count = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (chunk_count, vector_count, doc_id)
                )
                self.conn.commit()
                logger.info(f"Updated document {doc_id}: {chunk_count} chunks, {vector_count} vectors")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to update document: {e}")
            raise
    
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
