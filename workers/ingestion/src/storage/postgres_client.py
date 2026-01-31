import logging
import asyncpg
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PostgresStorage:
    """Update document metadata in PostgreSQL"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.connection_string)
            logger.info("Connected to PostgreSQL")
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Closed PostgreSQL connection")
    
    async def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None,
        chunk_count: Optional[int] = None
    ):
        """Update document processing status"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE documents
                    SET status = $1,
                        error_message = $2,
                        chunk_count = COALESCE($3, chunk_count),
                        processed_at = $4,
                        updated_at = $4
                    WHERE id = $5
                """
                
                await conn.execute(
                    query,
                    status,
                    error_message,
                    chunk_count,
                    datetime.utcnow(),
                    document_id
                )
                
                logger.info(f"Updated document {document_id} status to {status}")
        
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")
            raise
    
    async def get_document_info(self, document_id: str) -> Optional[dict]:
        """Get document information"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, filename, file_path, file_size, status, chunk_count
                    FROM documents
                    WHERE id = $1
                """
                
                row = await conn.fetchrow(query, document_id)
                
                if row:
                    return dict(row)
                return None
        
        except Exception as e:
            logger.error(f"Failed to get document info: {e}")
            return None
