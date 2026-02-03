import logging
import asyncio
import asyncpg
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class PostgresStorage:
    """Update document metadata in PostgreSQL"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self, max_retries: int = 5, retry_delay: int = 2):
        """Create connection pool with retry logic"""
        if not self.pool:
            for attempt in range(max_retries):
                try:
                    self.pool = await asyncpg.create_pool(self.connection_string)
                    logger.info("Connected to PostgreSQL")
                    return
                except Exception as e:
                    logger.warning(f"Failed to connect to PostgreSQL (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                    else:
                        raise
    
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
        chunk_count: Optional[int] = None,
        summary: Optional[str] = None,
        detected_languages: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        vector_count: Optional[int] = None,
        qa_pairs_count: Optional[int] = None
    ):
        """Update document processing status and metadata"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE documents
                    SET status = $1,
                        error_message = $2,
                        chunk_count = COALESCE($3, chunk_count),
                        processing_completed_at = $4,
                        updated_at = $4,
                        summary = COALESCE($5, summary),
                        detected_languages = COALESCE($6, detected_languages),
                        tags = COALESCE($7, tags),
                        vector_count = COALESCE($8, vector_count),
                        qa_pairs_count = COALESCE($9, qa_pairs_count)
                    WHERE id = $10
                """
                
                await conn.execute(
                    query,
                    status,
                    error_message,
                    chunk_count,
                    datetime.utcnow(),
                    summary,
                    detected_languages,
                    tags,
                    vector_count,
                    qa_pairs_count,
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
    
    async def get_setting(self, key: str) -> Optional[dict]:
        """Get setting value from database"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT value FROM settings WHERE key = $1"
                row = await conn.fetchrow(query, key)
                
                if row:
                    return row['value']
                return None
        
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
            return None
