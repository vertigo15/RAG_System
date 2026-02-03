"""
RabbitMQ Consumer for Document Converter Service.
"""

import logging
import json
import pika
from typing import Callable

logger = logging.getLogger(__name__)


class DocumentConverterConsumer:
    """RabbitMQ consumer for document conversion queue."""
    
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
            message: Dictionary containing chunking job details
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
