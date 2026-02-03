"""
Document Converter Service - Main Worker
Processes documents from RabbitMQ, converts to markdown, stores in MinIO.
"""

import logging
import json
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from config import settings
from consumer import DocumentConverterConsumer
from models import IncomingMessage, ChunkingMessage
from services.minio_service import MinIOService
from services.vision_service import VisionService
from services.llm_service import LLMService
from converters.text_converter import TextConverter
from converters.markdown_converter import MarkdownConverter
from converters.pdf_converter import PDFConverter
from router import ConverterRouter


class DocumentConverterWorker:
    """Main document converter worker."""
    
    def __init__(self):
        """Initialize worker with all services and converters."""
        logger.info("Initializing Document Converter Worker")
        
        # Initialize services
        self.minio_service = MinIOService(
            endpoint=f"{settings.minio_host}:{settings.minio_port}",
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            bucket_name=settings.minio_bucket,
            secure=settings.minio_secure
        )
        
        self.vision_service = VisionService(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.vision_deployment,
            timeout=settings.openai_timeout
        ) if settings.enable_image_descriptions else None
        
        self.llm_service = LLMService(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_llm_deployment,
            timeout=settings.openai_timeout
        ) if settings.enable_table_summaries else None
        
        # Initialize converters
        self.converters = {
            'txt': TextConverter(
                vision_service=self.vision_service,
                llm_service=self.llm_service
            ),
            'md': MarkdownConverter(
                vision_service=self.vision_service,
                llm_service=self.llm_service
            ),
            'markdown': MarkdownConverter(
                vision_service=self.vision_service,
                llm_service=self.llm_service
            ),
            'pdf': PDFConverter(
                doc_intelligence_endpoint=settings.azure_doc_intelligence_endpoint,
                doc_intelligence_key=settings.azure_doc_intelligence_key,
                vision_service=self.vision_service,
                llm_service=self.llm_service,
                enable_image_descriptions=settings.enable_image_descriptions
            ),
            # Note: DOCX and Excel converters need to be imported and added here
            # 'docx': DocxConverter(...),
            # 'xlsx': ExcelConverter(...),
            # 'xls': ExcelConverter(...),
        }
        
        # Initialize router
        self.router = ConverterRouter(self.converters)
        
        # Initialize consumer
        self.consumer = DocumentConverterConsumer(
            rabbitmq_url=settings.rabbitmq_url,
            input_queue=settings.document_processing_queue,
            output_queue=settings.chunking_queue
        )
        
        logger.info("Document Converter Worker initialized successfully")
    
    def process_document(self, message_data: dict):
        """
        Process a single document.
        
        Args:
            message_data: Parsed message from RabbitMQ
        """
        try:
            # Parse message
            message = IncomingMessage(**message_data)
            
            logger.info(f"Processing document: {message.document_id} - {message.original_filename}")
            
            # Read file
            with open(message.file_path, 'rb') as f:
                file_bytes = f.read()
            
            # Convert to markdown
            markdown, result = self.router.convert(
                file_bytes=file_bytes,
                filename=message.original_filename,
                document_id=message.document_id
            )
            
            if not result.success:
                logger.error(f"Conversion failed: {result.error}")
                # TODO: Update document status in PostgreSQL
                return
            
            # Upload markdown to MinIO
            markdown_path = self.minio_service.upload_markdown(
                document_id=message.document_id,
                markdown_content=markdown
            )
            
            logger.info(f"Markdown uploaded to: {markdown_path}")
            
            # Create chunking message
            chunking_message = ChunkingMessage(
                doc_id=message.document_id,
                markdown_path=markdown_path,
                original_filename=message.original_filename,
                file_type=result.file_type,
                image_count=result.image_count,
                table_count=result.table_count
            )
            
            # Publish to chunking queue
            self.consumer.publish_to_chunking_queue(chunking_message.model_dump())
            
            logger.info(f"Document conversion complete: {message.document_id}")
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}", exc_info=True)
            # TODO: Update document status to failed in PostgreSQL
            raise
    
    def on_message(self, ch, method, properties, body):
        """
        RabbitMQ message callback.
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        try:
            # Parse message
            message_data = json.loads(body.decode('utf-8'))
            
            # Process document
            self.process_document(message_data)
            
            # Acknowledge message
            self.consumer.ack_message(method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}", exc_info=True)
            
            # Negative acknowledge (don't requeue on persistent failures)
            self.consumer.nack_message(method.delivery_tag, requeue=False)
    
    def run(self):
        """Start the worker."""
        logger.info("Starting Document Converter Worker")
        logger.info(f"Supported file types: {list(self.converters.keys())}")
        logger.info(f"Listening on queue: {settings.document_processing_queue}")
        
        try:
            # Connect and start consuming
            self.consumer.connect()
            self.consumer.start_consuming(self.on_message)
            
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            # Cleanup
            self.consumer.stop_consuming()
            logger.info("Document Converter Worker stopped")


def main():
    """Entry point."""
    try:
        worker = DocumentConverterWorker()
        worker.run()
    except Exception as e:
        logger.error(f"Failed to start worker: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
