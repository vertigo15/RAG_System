"""
RabbitMQ Consumer
Consumes chunking jobs from chunking queue.
"""

import logging
import json
import pika
from typing import Callable

logger = logging.getLogger(__name__)


class ChunkingConsumer:
    """RabbitMQ consumer for chunking queue."""
    
    def __init__(self, rabbitmq_url: str, queue_name: str):
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish RabbitMQ connection."""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            # Set QoS
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"Connected to RabbitMQ, listening on: {self.queue_name}")
        except Exception as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            raise
    
    def start_consuming(self, callback: Callable):
        """Start consuming messages."""
        try:
            self.channel.basic_consume(
                queue=self.queue_name,
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
    
    def ack_message(self, delivery_tag):
        """Acknowledge message processing."""
        self.channel.basic_ack(delivery_tag=delivery_tag)
    
    def nack_message(self, delivery_tag, requeue=True):
        """Negative acknowledge (reject) message."""
        self.channel.basic_nack(delivery_tag=delivery_tag, requeue=requeue)


def parse_message(body: bytes) -> dict:
    """Parse incoming message body."""
    try:
        message = json.loads(body.decode('utf-8'))
        logger.info(f"Parsed message for document: {message.get('doc_id')}")
        return message
    except Exception as e:
        logger.error(f"Failed to parse message: {e}")
        raise
