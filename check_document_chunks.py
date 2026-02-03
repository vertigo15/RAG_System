"""
Check document chunks and their types in the database.
"""
import asyncio
import asyncpg
from collections import Counter

async def check_documents():
    """Check recent documents and their chunk types."""
    
    # Connect to PostgreSQL
    conn = await asyncpg.connect('postgresql://rag_user:secure_password@localhost:5432/rag_db')
    
    # Get recent documents
    docs = await conn.fetch('''
        SELECT id, filename, status, chunk_count, qa_pairs_count, created_at
        FROM documents 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    
    print("=" * 80)
    print("Recent Documents")
    print("=" * 80)
    
    for doc in docs:
        print(f"\nDocument: {doc['filename']}")
        print(f"  ID: {doc['id']}")
        print(f"  Status: {doc['status']}")
        print(f"  Total chunks: {doc['chunk_count']}")
        print(f"  Q&A pairs: {doc['qa_pairs_count']}")
        print(f"  Created: {doc['created_at']}")
    
    # Check if we can connect to Qdrant
    try:
        from qdrant_client import QdrantClient
        
        print("\n" + "=" * 80)
        print("Checking Qdrant for chunk types")
        print("=" * 80)
        
        client = QdrantClient(host="localhost", port=6333)
        
        # Get collection info
        try:
            collection_info = client.get_collection("chunks")
            print(f"\nQdrant collection 'chunks': {collection_info.points_count} points")
        except Exception as e:
            print(f"\nCould not get collection info: {e}")
            await conn.close()
            return
        
        # For each document, check chunk types
        for doc in docs[:3]:  # Check first 3 docs
            doc_id = str(doc['id'])
            print(f"\n--- Document: {doc['filename']} ---")
            
            # Search for all chunks of this document
            results = client.scroll(
                collection_name="chunks",
                scroll_filter={
                    "must": [
                        {
                            "key": "document_id",
                            "match": {"value": doc_id}
                        }
                    ]
                },
                limit=1000
            )
            
            points = results[0]
            
            if not points:
                print(f"  No chunks found in Qdrant")
                continue
            
            # Count by type
            type_counts = Counter()
            language_counts = Counter()
            multilingual_count = 0
            
            for point in points:
                payload = point.payload
                chunk_type = payload.get('type', 'unknown')
                language = payload.get('language', 'unknown')
                is_multilingual = payload.get('is_multilingual', False)
                
                type_counts[chunk_type] += 1
                language_counts[language] += 1
                if is_multilingual:
                    multilingual_count += 1
            
            print(f"  Total chunks in Qdrant: {len(points)}")
            print(f"  Chunk types:")
            for chunk_type, count in type_counts.most_common():
                print(f"    - {chunk_type}: {count}")
            
            print(f"  Languages:")
            for lang, count in language_counts.most_common():
                print(f"    - {lang}: {count}")
            
            print(f"  Multilingual chunks: {multilingual_count}")
            
            # Show sample of each type
            print(f"\n  Sample chunks:")
            for chunk_type in type_counts.keys():
                sample = next((p for p in points if p.payload.get('type') == chunk_type), None)
                if sample:
                    text = sample.payload.get('text', '')[:100]
                    print(f"    [{chunk_type}]: {text}...")
    
    except Exception as e:
        print(f"\nError checking Qdrant: {e}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_documents())
