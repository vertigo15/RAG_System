"""
Script to requeue pending documents that were lost during worker restart.
"""
import asyncio
import asyncpg
import aio_pika
import json
import os

async def main():
    # Database connection
    db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'rag_user')}:{os.getenv('POSTGRES_PASSWORD', 'rag_password_123')}@localhost:5433/rag_system"
    
    # RabbitMQ connection
    rabbitmq_url = "amqp://guest:guest@localhost:5672/"
    
    # Connect to database
    conn = await asyncpg.connect(db_url)
    
    try:
        # Get pending or failed documents
        pending_docs = await conn.fetch("""
            SELECT id, filename, status
            FROM documents
            WHERE status IN ('pending', 'failed')
            ORDER BY uploaded_at DESC
        """)
        
        print(f"Found {len(pending_docs)} documents to requeue (pending/failed)")
        
        if not pending_docs:
            print("No documents to requeue")
            return
        
        # Reset status to pending
        for doc in pending_docs:
            await conn.execute("""
                UPDATE documents
                SET status = 'pending', error_message = NULL
                WHERE id = $1
            """, doc['id'])
        
        # Connect to RabbitMQ
        connection = await aio_pika.connect_robust(rabbitmq_url)
        channel = await connection.channel()
        
        # Requeue each document
        for doc in pending_docs:
            doc_id = str(doc['id'])
            filename = doc['filename']
            file_path = f"/app/uploads/{doc_id}_{filename}"
            
            message_body = {
                "document_id": doc_id,
                "file_path": file_path,
                "correlation_id": ""
            }
            
            message = aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await channel.default_exchange.publish(
                message,
                routing_key="ingestion_queue"
            )
            
            print(f"✓ Requeued: {filename} ({doc_id})")
        
        await connection.close()
        print(f"\n✅ Successfully requeued {len(pending_docs)} documents")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
