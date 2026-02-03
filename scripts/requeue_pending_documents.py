"""
Script to requeue pending documents to RabbitMQ.
Run this to process documents that are stuck in 'pending' status.
"""

import asyncio
import asyncpg
import aio_pika
import json
import os
from pathlib import Path

# Configuration from environment
POSTGRES_USER = os.getenv("POSTGRES_USER", "rag_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")  # External port
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag_system")

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

INGESTION_QUEUE = "ingestion_queue"
UPLOAD_DIR = "/app/uploads"  # Use string, not Path object


async def get_pending_documents(conn):
    """Get all pending documents from database."""
    query = """
        SELECT id, filename 
        FROM documents 
        WHERE processing_status = 'pending'
        ORDER BY created_at
    """
    rows = await conn.fetch(query)
    return rows


async def publish_to_queue(channel, document_id, file_path):
    """Publish document to ingestion queue."""
    # Extract filename from path string
    filename_with_id = file_path.split('/')[-1] if '/' in file_path else file_path
    original_filename = filename_with_id.split('_', 1)[1] if '_' in filename_with_id else filename_with_id
    
    message_body = {
        "document_id": str(document_id),
        "file_path": file_path,  # Already a string with forward slashes
        "original_filename": original_filename,
        "correlation_id": f"requeue-{document_id}"
    }
    
    message = aio_pika.Message(
        body=json.dumps(message_body).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    
    await channel.default_exchange.publish(
        message,
        routing_key=INGESTION_QUEUE
    )
    
    print(f"✓ Queued: {document_id} - {message_body['original_filename']}")


async def main():
    """Main function to requeue pending documents."""
    print("Requeuing Pending Documents")
    print("=" * 50)
    
    # Connect to PostgreSQL
    print(f"\nConnecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}...")
    pg_conn = await asyncpg.connect(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB
    )
    print("✓ Connected to PostgreSQL")
    
    # Connect to RabbitMQ
    print(f"\nConnecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}...")
    rabbitmq_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
    connection = await aio_pika.connect_robust(rabbitmq_url)
    channel = await connection.channel()
    
    # Declare queue
    await channel.declare_queue(INGESTION_QUEUE, durable=True)
    print("✓ Connected to RabbitMQ")
    
    # Get pending documents
    print("\nFetching pending documents...")
    documents = await get_pending_documents(pg_conn)
    print(f"Found {len(documents)} pending documents\n")
    
    if not documents:
        print("No pending documents to process!")
        return
    
    # Requeue each document
    print("Requeuing documents:")
    print("-" * 50)
    
    requeued = 0
    failed = 0
    
    for doc in documents:
        doc_id = doc['id']
        filename = doc['filename']
        
        # Construct file path with forward slashes for Linux containers
        file_path = f"{UPLOAD_DIR}/{doc_id}_{filename}"
        
        try:
            await publish_to_queue(channel, doc_id, file_path)
            requeued += 1
        except Exception as e:
            print(f"✗ Failed to queue {doc_id}: {e}")
            failed += 1
    
    print("-" * 50)
    print(f"\nSummary:")
    print(f"  Requeued: {requeued}")
    print(f"  Failed:   {failed}")
    print(f"  Total:    {len(documents)}")
    
    # Cleanup
    await pg_conn.close()
    await connection.close()
    
    print("\n✓ Done!")


if __name__ == "__main__":
    asyncio.run(main())
