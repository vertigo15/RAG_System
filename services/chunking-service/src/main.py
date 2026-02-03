"""
Chunking & Embedding Service
Main entry point for the chunking and embedding worker.
"""

import logging
import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shared"))

from config import settings
from consumer import ChunkingConsumer, parse_message
from storage.postgres_client import PostgreSQLClient
from storage.minio_storage import create_minio_storage
from storage.qdrant_client import QdrantClient
from pipeline.chunker import Chunker
from pipeline.embedder import Embedder

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChunkingService:
    """Main chunking and embedding pipeline."""
    
    def __init__(self):
        # Initialize components
        self.pg_client = PostgreSQLClient(settings.postgres_url)
        self.minio_client = create_minio_storage(
            host=settings.minio_host,
            port=settings.minio_port,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            bucket_name=settings.minio_bucket,
            secure=settings.minio_secure
        )
        self.qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection_name=settings.qdrant_collection
        )
        
        # Pipeline components
        self.chunker = Chunker()
        self.embedder = Embedder(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            deployment_name=settings.azure_embedding_deployment,
            batch_size=settings.embedding_batch_size
        )
        
        # RabbitMQ consumer
        self.consumer = ChunkingConsumer(
            rabbitmq_url=settings.rabbitmq_url,
            queue_name=settings.chunking_queue
        )
        
        logger.info("Chunking Service initialized")
    
    def process_document(self, message: dict) -> None:
        """
        Process a document through chunking and embedding pipeline.
        
        Pipeline:
        1. Fetch markdown and metadata from MinIO
        2. Chunk document using specified strategy
        3. Generate embeddings for chunks
        4. Fetch summary and Q&A pairs from MinIO
        5. Generate embeddings for summary and Q&A
        6. Store all vectors in Qdrant
        7. Update PostgreSQL
        """
        doc_id = message["doc_id"]
        minio_path = message["minio_path"]
        chunking_strategy = message.get("chunking_strategy", "auto")
        chunk_size = message.get("chunk_size", settings.default_chunk_size)
        chunk_overlap = message.get("chunk_overlap", settings.default_chunk_overlap)
        
        logger.info(f"Processing document: {doc_id}")
        
        try:
            # Update status
            self.pg_client.update_document_status(doc_id, "chunking")
            
            # Step 1: Fetch markdown from MinIO
            logger.info("Fetching document from MinIO")
            markdown = self.minio_client.retrieve_text(f"{minio_path}document.md")
            
            # Step 2: Chunk document
            logger.info(f"Chunking document (strategy: {chunking_strategy})")
            chunks = self.chunker.chunk(
                text=markdown,
                strategy=chunking_strategy,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 3: Generate embeddings for chunks
            logger.info("Generating chunk embeddings")
            embedded_chunks = self.embedder.embed_chunks(chunks)
            
            # Step 4: Fetch summary and Q&A from MinIO
            logger.info("Fetching summary and Q&A pairs")
            summary = self.minio_client.retrieve_text(f"{minio_path}summary.md")
            qa_pairs_data = self.minio_client.retrieve_json(f"{minio_path}qa_pairs.json")
            qa_pairs = qa_pairs_data.get("qa_pairs", [])
            
            # Step 5: Generate embeddings for summary and Q&A
            logger.info("Generating summary and Q&A embeddings")
            summary_embedding, qa_with_embeddings = self.embedder.embed_summary_and_qa(
                summary=summary,
                qa_pairs=qa_pairs
            )
            
            # Step 6: Store all vectors in Qdrant
            logger.info("Storing vectors in Qdrant")
            
            # Store chunks
            chunk_count = self.qdrant_client.store_chunks(doc_id, embedded_chunks)
            
            # Store summary
            self.qdrant_client.store_summary(doc_id, summary, summary_embedding)
            
            # Store Q&A pairs
            qa_vector_count = self.qdrant_client.store_qa_pairs(doc_id, qa_with_embeddings)
            
            # Calculate total vectors
            total_vectors = chunk_count + 1 + qa_vector_count  # chunks + summary + Q&A
            
            logger.info(f"Stored {total_vectors} vectors total")
            
            # Step 7: Update PostgreSQL
            self.pg_client.update_document_chunking_complete(
                doc_id=doc_id,
                chunk_count=len(chunks),
                vector_count=total_vectors
            )
            
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
            
            # Negative acknowledge (don't requeue)
            self.consumer.nack_message(method.delivery_tag, requeue=False)
    
    def run(self):
        """Start the chunking service worker."""
        logger.info("Starting Chunking & Embedding Service")
        
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
            logger.info("Chunking & Embedding Service stopped")


def main():
    """Entry point."""
    service = ChunkingService()
    service.run()


if __name__ == "__main__":
    main()
