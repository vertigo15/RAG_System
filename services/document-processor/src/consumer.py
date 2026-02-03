"""
RabbitMQ Consumer
Consumes document processing jobs and publishes to chunking queue.
"""

import logging
import json
import os
import pika
from typing import Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentProcessingConsumer:
    """RabbitMQ consumer for document processing queue."""
    
    def __init__(
        self,
        rabbitmq_url: str,
        input_queue: str,
        output_queue: str
    ):
        self.rabbitmq_url = rabbitmq_url
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish RabbitMQ connection."""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=self.input_queue, durable=True)
            self.channel.queue_declare(queue=self.output_queue, durable=True)
            
            # Set QoS (prefetch count)
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ, listening on: {self.input_queue}")
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            raise
    
    def start_consuming(self, callback: Callable):
        """
        Start consuming messages.
        
        Args:
            callback: Function to process messages
                      Signature: callback(ch, method, properties, body) -> None
        """
        try:
            self.channel.basic_consume(
                queue=self.input_queue,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info("Started consuming messages")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
    
    def stop_consuming(self):
        """Stop consuming messages."""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        logger.info("Consumer stopped")
    
    def publish_to_chunking_queue(self, message: dict):
        """
        Publish message to chunking queue.
        
        Args:
            message: Dictionary containing:
                {
                    "doc_id": "uuid",
                    "minio_path": "documents/uuid/",
                    "chunking_strategy": "auto|simple|semantic|hierarchical",
                    "chunk_size": 500,
                    "chunk_overlap": 50,
                    "metadata": {...}
                }
        """
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.output_queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Persistent
                    content_type='application/json'
                )
            )
            logger.info(f"Published to chunking queue: {message['doc_id']}")
        except Exception as e:
            logger.error(f"Failed to publish to chunking queue: {e}")
            raise
    
    def ack_message(self, delivery_tag):
        """Acknowledge message processing."""
        self.channel.basic_ack(delivery_tag=delivery_tag)
    
    def nack_message(self, delivery_tag, requeue=True):
        """Negative acknowledge (reject) message."""
        self.channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)


def parse_message(body: bytes) -> dict:
    """
    Parse incoming message body.
    
    Expected format from backend:
    {
        "document_id": "uuid",
        "file_path": "/app/uploads/xxx.pdf",
        "correlation_id": "..."
    }
    """
    try:
        message = json.loads(body.decode('utf-8'))
        
        # Map backend field names to processor field names
        if "document_id" in message:
            message["doc_id"] = message["document_id"]
        
        # Extract filename from file_path if not provided
        if "file_path" in message and "original_filename" not in message:
            message["original_filename"] = os.path.basename(message["file_path"])
        
        logger.info(f"Parsed message for document: {message.get('doc_id')}")
        return message
    except Exception as e:
        logger.error(f"Failed to parse message: {e}")
        raise


def build_chunking_message(
    doc_id: str,
    minio_path: str,
    metadata: dict
) -> dict:
    """
    Build message for chunking queue.
    
    Args:
        doc_id: Document UUID
        minio_path: MinIO storage path
        metadata: Complete document metadata
    
    Returns:
        Message dictionary for chunking service
    """
    return {
        "doc_id": doc_id,
        "minio_path": minio_path,
        "chunking_strategy": metadata["chunking"]["recommended_strategy"],
        "chunk_size": metadata["chunking"]["recommended_chunk_size"],
        "chunk_overlap": metadata["chunking"]["recommended_overlap"],
        "metadata": {
            "size_category": metadata["document"]["size_category"],
            "token_count": metadata["document"]["token_count"],
            "primary_language": metadata["language"]["primary"],
            "is_multilingual": metadata["language"]["is_multilingual"]
        }
    }
