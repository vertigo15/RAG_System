"""
RabbitMQ queue service for job publishing.
"""

import json
import aio_pika
from typing import Dict, Any
from src.core.logging import get_logger, correlation_id_var
from src.core.exceptions import QueueError
from src.core.constants import INGESTION_QUEUE, QUERY_QUEUE

logger = get_logger(__name__)


class QueueService:
    """Service for RabbitMQ operations."""
    
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
    
    async def connect(self) -> None:
        """Connect to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Declare queues
            await self.channel.declare_queue(INGESTION_QUEUE, durable=True)
            await self.channel.declare_queue(QUERY_QUEUE, durable=True)
            
            logger.info("Connected to RabbitMQ successfully")
        except Exception as e:
            logger.exception("Failed to connect to RabbitMQ")
            raise QueueError("Failed to connect to RabbitMQ", "connection", error=str(e))
    
    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
    
    async def publish_ingestion_job(
        self,
        document_id: str,
        file_path: str
    ) -> None:
        """Publish document ingestion job."""
        if not self.channel:
            raise QueueError("Not connected to RabbitMQ", INGESTION_QUEUE)
        
        message_body = {
            "document_id": document_id,
            "file_path": file_path,
            "correlation_id": correlation_id_var.get('')
        }
        
        try:
            message = aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await self.channel.default_exchange.publish(
                message,
                routing_key=INGESTION_QUEUE
            )
            
            logger.info(
                "Ingestion job published",
                document_id=document_id,
                queue=INGESTION_QUEUE
            )
        except Exception as e:
            logger.exception("Failed to publish ingestion job", document_id=document_id)
            raise QueueError(
                "Failed to publish ingestion job",
                INGESTION_QUEUE,
                document_id=document_id,
                error=str(e)
            )
    
    async def publish_query_job(
        self,
        query_id: str,
        query_text: str,
        document_filter: list = None,
        debug_mode: bool = False,
        top_k: int = 10,
        rerank_top: int = 5
    ) -> None:
        """Publish query processing job."""
        if not self.channel:
            raise QueueError("Not connected to RabbitMQ", QUERY_QUEUE)
        
        message_body = {
            "query_id": query_id,
            "query_text": query_text,
            "document_filter": document_filter,
            "debug_mode": debug_mode,
            "top_k": top_k,
            "rerank_top": rerank_top,
            "correlation_id": correlation_id_var.get('')
        }
        
        try:
            message = aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await self.channel.default_exchange.publish(
                message,
                routing_key=QUERY_QUEUE
            )
            
            logger.info(
                "Query job published",
                query_id=query_id,
                queue=QUERY_QUEUE
            )
        except Exception as e:
            logger.exception("Failed to publish query job", query_id=query_id)
            raise QueueError(
                "Failed to publish query job",
                QUERY_QUEUE,
                query_id=query_id,
                error=str(e)
            )
