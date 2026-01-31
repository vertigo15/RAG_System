import asyncio
import json
import logging
from typing import Dict, Any

from aio_pika import connect_robust, IncomingMessage
from config import settings
from pipeline.document_intelligence import DocumentIntelligenceProcessor
from pipeline.vision_processor import VisionProcessor
from pipeline.tree_builder import TreeBuilder
from pipeline.enrichment import Enrichment
from pipeline.chunker import Chunker
from pipeline.embedder import Embedder
from storage.qdrant_client import QdrantStorage
from storage.postgres_client import PostgresStorage

logger = logging.getLogger(__name__)

class IngestionConsumer:
    """Consume document ingestion jobs from RabbitMQ"""
    
    def __init__(self):
        self.settings = settings
        
        # Initialize pipeline stages
        self.doc_intelligence = DocumentIntelligenceProcessor(
            endpoint=settings.azure_doc_intelligence_endpoint,
            key=settings.azure_doc_intelligence_key
        )
        
        self.vision_processor = VisionProcessor(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_gpt4,
            api_version=settings.azure_openai_api_version
        )
        
        self.tree_builder = TreeBuilder()
        
        self.enrichment = Enrichment(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_gpt4,
            api_version=settings.azure_openai_api_version
        )
        
        self.chunker = Chunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        self.embedder = Embedder(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_embed,
            api_version=settings.azure_openai_api_version
        )
        
        # Initialize storage clients
        self.qdrant_storage = QdrantStorage(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection=settings.qdrant_collection
        )
        
        self.postgres_storage = PostgresStorage(
            connection_string=settings.postgres_url
        )
    
    async def process_document(self, job_data: Dict[str, Any]):
        """
        Process a document through the full ingestion pipeline
        
        Pipeline stages:
        1. Document Intelligence - Extract text and structure
        2. Vision Processing - Analyze images/charts
        3. Tree Building - Create hierarchical structure
        4. Enrichment - Generate summaries and Q&A
        5. Chunking - Create semantic chunks
        6. Embedding - Generate vector embeddings
        7. Storage - Store in Qdrant and update PostgreSQL
        """
        document_id = job_data.get("document_id")
        file_path = job_data.get("file_path")
        
        logger.info(f"Starting ingestion for document {document_id}: {file_path}")
        
        try:
            # Update status to processing
            await self.postgres_storage.update_document_status(document_id, "processing")
            
            # Stage 1: Document Intelligence
            logger.info("[1/7] Document Intelligence extraction")
            extracted_data = await self.doc_intelligence.process(file_path)
            
            # Stage 2: Vision Processing
            logger.info("[2/7] Vision processing")
            image_descriptions = await self.vision_processor.process_images(
                extracted_data.get("pages", []),
                file_path
            )
            
            # Stage 3: Tree Building
            logger.info("[3/7] Building document tree")
            tree = self.tree_builder.build_tree(extracted_data, image_descriptions)
            
            # Stage 4: Enrichment
            logger.info("[4/7] Enriching with summaries and Q&A")
            enriched_tree = await self.enrichment.enrich_document(tree)
            
            # Stage 5: Chunking
            logger.info("[5/7] Chunking document")
            chunks = self.chunker.chunk_document(enriched_tree)
            
            # Stage 6: Embedding
            logger.info("[6/7] Generating embeddings")
            embedded_chunks = await self.embedder.generate_embeddings(chunks)
            
            # Stage 7: Storage
            logger.info("[7/7] Storing in Qdrant and PostgreSQL")
            chunk_count = await self.qdrant_storage.store_chunks(document_id, embedded_chunks)
            
            # Update document status to completed
            await self.postgres_storage.update_document_status(
                document_id,
                "completed",
                chunk_count=chunk_count
            )
            
            logger.info(f"Successfully processed document {document_id} with {chunk_count} chunks")
        
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}", exc_info=True)
            
            # Update document status to failed
            await self.postgres_storage.update_document_status(
                document_id,
                "failed",
                error_message=str(e)
            )
    
    async def on_message(self, message: IncomingMessage):
        """Handle incoming RabbitMQ message"""
        async with message.process():
            try:
                # Parse job data
                job_data = json.loads(message.body.decode())
                logger.info(f"Received job: {job_data}")
                
                # Process document
                await self.process_document(job_data)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def start(self):
        """Start consuming from RabbitMQ"""
        logger.info("Starting ingestion worker")
        
        # Connect to PostgreSQL
        await self.postgres_storage.connect()
        
        # Connect to RabbitMQ
        connection = await connect_robust(self.settings.rabbitmq_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        # Declare queue
        queue = await channel.declare_queue("document_ingestion", durable=True)
        
        # Start consuming
        logger.info("Waiting for messages from document_ingestion queue")
        await queue.consume(self.on_message)
        
        # Keep running
        try:
            await asyncio.Future()
        finally:
            await connection.close()
            await self.postgres_storage.close()
