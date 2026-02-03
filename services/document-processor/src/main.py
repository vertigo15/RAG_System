"""
Document Processor Service
Main entry point for the document processing worker.
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from config import settings
from consumer import (
    DocumentProcessingConsumer,
    parse_message,
    build_chunking_message
)
from storage.postgres_client import PostgreSQLClient
from storage.minio_storage import create_minio_storage
from pipeline.markdown_converter import MarkdownConverter
from pipeline.metadata_extractor import MetadataExtractor
from pipeline.strategy_selector import StrategySelector
from pipeline.summarizer import Summarizer
from pipeline.qa_generator import QAGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main document processing pipeline."""
    
    def __init__(self):
        # Initialize components
        self.pg_client = PostgreSQLClient(settings.postgres_url)
        self.minio_storage = create_minio_storage(
            host=settings.minio_host,
            port=settings.minio_port,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            bucket_name=settings.minio_bucket,
            secure=settings.minio_secure
        )
        
        # Pipeline components
        self.markdown_converter = MarkdownConverter()
        self.metadata_extractor = MetadataExtractor()
        self.strategy_selector = StrategySelector()
        self.summarizer = Summarizer(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_llm_deployment
        )
        self.qa_generator = QAGenerator(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_llm_deployment
        )
        
        # RabbitMQ consumer
        self.consumer = DocumentProcessingConsumer(
            rabbitmq_url=settings.rabbitmq_url,
            input_queue=settings.document_processing_queue,
            output_queue=settings.chunking_queue
        )
        
        logger.info("Document Processor initialized")
    
    def process_document(self, message: dict) -> None:
        """
        Process a document through the full pipeline.
        
        Pipeline:
        1. Extract with Azure Document Intelligence (reuse from uploaded doc)
        2. Convert to Markdown
        3. Extract Metadata (language, tokens, structure)
        4. Select Strategies
        5. Generate Summary
        6. Generate Q&A pairs
        7. Store in MinIO
        8. Update PostgreSQL
        9. Publish to Chunking Queue
        """
        doc_id = message["doc_id"]
        file_path = message["file_path"]
        original_filename = message["original_filename"]
        
        start_time = datetime.utcnow()
        
        logger.info(f"Processing document: {doc_id} - {original_filename}")
        
        try:
            # Update status to processing
            self.pg_client.update_document_status(doc_id, "processing")
            
            # Step 1: Extract with Azure Document Intelligence
            # (This is done by backend before queuing, so we load from file)
            logger.info("Loading document for processing")
            
            # For now, we'll use a simplified approach
            # In production, the backend would include doc_intelligence_result in the message
            # or we'd run it here. For this implementation, we'll assume text extraction
            from azure.ai.formrecognizer import DocumentAnalysisClient
            from azure.core.credentials import AzureKeyCredential
            
            doc_client = DocumentAnalysisClient(
                endpoint=settings.azure_doc_intelligence_endpoint,
                credential=AzureKeyCredential(settings.azure_doc_intelligence_key)
            )
            
            with open(file_path, "rb") as f:
                poller = doc_client.begin_analyze_document("prebuilt-layout", document=f)
            
            result = poller.result()
            
            # Build doc intelligence result dict
            doc_intelligence_result = {
                "text": result.content,
                "pages": [
                    {
                        "page_number": p.page_number,
                        "width": p.width,
                        "height": p.height,
                        "lines": [{"text": line.content} for line in (p.lines or [])]
                    }
                    for p in result.pages
                ],
                "tables": [
                    {
                        "row_count": t.row_count,
                        "column_count": t.column_count,
                        "cells": [
                            {
                                "row_index": c.row_index,
                                "column_index": c.column_index,
                                "content": c.content
                            }
                            for c in t.cells
                        ]
                    }
                    for t in (result.tables or [])
                ],
                "paragraphs": [
                    {
                        "content": p.content,
                        "role": getattr(p, 'role', None)
                    }
                    for p in (result.paragraphs or [])
                ]
            }
            
            logger.info("Document Intelligence extraction complete")
            
            # Step 2: Convert to Markdown
            markdown = self.markdown_converter.convert(doc_intelligence_result)
            logger.info(f"Converted to Markdown ({len(markdown)} chars)")
            
            # Step 3: Extract Metadata
            # Get file stats
            file_stats = os.stat(file_path)
            mime_type = message.get("mime_type", "application/pdf")
            
            metadata = self.metadata_extractor.extract(
                doc_id=doc_id,
                original_filename=original_filename,
                file_size_bytes=file_stats.st_size,
                mime_type=mime_type,
                markdown=markdown,
                doc_intelligence_result=doc_intelligence_result
            )
            
            logger.info(
                f"Metadata extracted: {metadata['document']['size_category']} "
                f"({metadata['document']['token_count']} tokens)"
            )
            
            # Step 4: Select Strategies
            strategies = self.strategy_selector.select_strategies(metadata)
            
            # Step 5: Generate Summary
            sections = self.markdown_converter.extract_sections(markdown)
            summary = self.summarizer.summarize(
                markdown=markdown,
                sections=sections,
                method=strategies["summary_method"],
                metadata=metadata
            )
            
            logger.info(f"Summary generated ({len(summary)} chars)")
            
            # Step 6: Generate Q&A pairs
            num_qa = self.strategy_selector.get_num_qa_pairs(
                metadata["document"]["size_category"]
            )
            
            qa_pairs = self.qa_generator.generate(
                markdown=markdown,
                sections=sections,
                method=strategies["qa_method"],
                num_questions=num_qa,
                metadata=metadata
            )
            
            logger.info(f"Generated {len(qa_pairs)} Q&A pairs")
            
            # Update metadata with enrichment info
            self.metadata_extractor.update_enrichment(
                metadata=metadata,
                summary_method=strategies["summary_method"],
                summary_sections_count=len(sections) if strategies["summary_method"] == "map_reduce" else 1,
                qa_method=strategies["qa_method"],
                qa_pairs_count=len(qa_pairs)
            )
            
            # Finalize metadata
            self.metadata_extractor.finalize(metadata, start_time)
            
            # Step 7: Store in MinIO
            minio_path = self.minio_storage.store_document_files(
                doc_id=doc_id,
                original_file_path=file_path,
                markdown=markdown,
                metadata=metadata,
                summary=summary,
                qa_pairs=qa_pairs
            )
            
            logger.info(f"Stored files in MinIO: {minio_path}")
            
            # Step 8: Update PostgreSQL
            self.pg_client.update_document_metadata(
                doc_id=doc_id,
                minio_path=minio_path,
                metadata=metadata
            )
            
            logger.info("Updated PostgreSQL metadata")
            
            # Step 9: Publish to Chunking Queue
            chunking_message = build_chunking_message(
                doc_id=doc_id,
                minio_path=minio_path,
                metadata=metadata
            )
            
            self.consumer.publish_to_chunking_queue(chunking_message)
            
            logger.info(f"Document processing complete: {doc_id}")
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}", exc_info=True)
            
            # Update status to failed
            self.pg_client.update_document_status(
                doc_id=doc_id,
                processing_status="failed",
                error_message=str(e)
            )
            
            raise
    
    def on_message(self, ch, method, properties, body):
        """RabbitMQ message callback."""
        try:
            message = parse_message(body)
            self.process_document(message)
            
            # Acknowledge message
            self.consumer.ack_message(method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            
            # Negative acknowledge (requeue)
            self.consumer.nack_message(method.delivery_tag, requeue=False)
    
    def run(self):
        """Start the document processor worker."""
        logger.info("Starting Document Processor service")
        
        try:
            # Connect to databases
            self.pg_client.connect()
            
            # Connect to RabbitMQ and start consuming
            self.consumer.connect()
            self.consumer.start_consuming(self.on_message)
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            # Cleanup
            self.consumer.stop_consuming()
            self.pg_client.close()
            logger.info("Document Processor service stopped")


def main():
    """Entry point."""
    processor = DocumentProcessor()
    processor.run()


if __name__ == "__main__":
    main()
