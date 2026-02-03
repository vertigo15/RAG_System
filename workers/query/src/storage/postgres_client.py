import logging
import asyncio
import asyncpg
import json
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PostgresStorage:
    """Update query results in PostgreSQL"""
    
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
    
    async def update_query_result(
        self,
        query_id: str,
        status: str,
        answer: Optional[str] = None,
        citations: Optional[list] = None,
        debug_data: Optional[dict] = None,
        error_message: Optional[str] = None
    ):
        """Update query with results"""
        if not self.pool:
            await self.connect()
        
        try:
            async with self.pool.acquire() as conn:
                query_sql = """
                    UPDATE queries
                    SET status = $1,
                        answer = COALESCE($2, answer),
                        citations = COALESCE($3, citations),
                        debug_data = COALESCE($4, debug_data),
                        error_message = $5,
                        completed_at = $6,
                        updated_at = $6
                    WHERE id = $7
                """
                
                await conn.execute(
                    query_sql,
                    status,
                    answer,
                    json.dumps(citations) if citations else None,
                    json.dumps(debug_data) if debug_data else None,
                    error_message,
                    datetime.utcnow(),
                    query_id
                )
                
                logger.info(f"Updated query {query_id} status to {status}")
        
        except Exception as e:
            logger.error(f"Failed to update query result: {e}")
            raise
