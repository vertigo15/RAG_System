# How to Check Chunk Types for Documents

## UI Method (Easiest)

### 1. Start Docker
```bash
docker-compose up -d
```

### 2. Access Frontend
- Open: http://localhost:3000
- Go to "Documents" page
- Find your document "הפתוחה.pdf"
- Click "View Chunks" button

### 3. Filter by Type
You'll now see **filter buttons** at the top:
- **All** - Shows all chunks with count
- **Text** - Only text chunks (blue)
- **Summaries** - Only summary chunks (green)
- **Q&A** - Only Q&A pairs (purple)

Each button shows the count for that type, e.g.:
```
All (45)  Text (30)  Summaries (6)  Q&A (9)
```

## Command Line Method

### Using the check script:
```bash
python check_document_chunks.py
```

This will show:
```
--- Document: הפתוחה.pdf ---
  Total chunks in Qdrant: 45
  Chunk types:
    - text_chunk: 30
    - summary: 6
    - qa: 9
  
  Languages:
    - he: 35
    - en: 10
  
  Multilingual chunks: 8
  
  Sample chunks:
    [text_chunk]: האוניברסיטה הפתוחה היא מוסד להשכלה גבוהה...
    [summary]: סיכום: מסמך זה מתאר את...
    [qa]: Q: מהי האוניברסיטה הפתוחה?\nA: מוסד אקדמי המאפשר...
```

## What to Expect

A typical document will have:

### Text Chunks (type: `text_chunk`)
- Most of the chunks
- Main document content
- Overlapping chunks (512 tokens each)
- Example count: 20-50 chunks for a 20-page document

### Summaries (type: `summary`)
- 1 document-level summary
- 1 summary per section
- Example count: 3-10 summaries
- Located in metadata with `level: "document"` or `level: "section"`

### Q&A Pairs (type: `qa`)
- Generated questions and answers
- Format: "Q: ... \nA: ..."
- Example count: 5-15 Q&A pairs
- Each pair is a separate chunk

## Verifying All Types Are Present

Your document **"הפתוחה.pdf"** should have all three types if:

✅ Ingestion completed successfully (status: `completed`)
✅ Enrichment stage ran (generates summaries and Q&A)
✅ Chunks were stored in Qdrant

To verify:
1. Check document status in UI or database
2. Look for `chunk_count > 0`
3. Look for `qa_pairs_count > 0`
4. Use the chunk viewer with type filters

## If Types Are Missing

### No Q&A or Summaries
**Cause**: Enrichment stage might have failed or been skipped

**Solution**:
1. Check worker logs: `docker-compose logs ingestion_worker`
2. Look for errors in Stage 4 (Enrichment)
3. Re-upload the document to retry processing

### No Text Chunks
**Cause**: Document Intelligence extraction failed

**Solution**:
1. Check if file is valid PDF/DOCX
2. Check Azure Document Intelligence quota/credentials
3. Review worker logs for errors

### Only One Type
**Cause**: Partial pipeline failure

**Solution**:
1. Delete the document
2. Re-upload to trigger full pipeline
3. Monitor logs during processing

## Database Query (Advanced)

If you want to query PostgreSQL directly:

```sql
-- Connect to database
docker exec -it rag_system-postgres-1 psql -U rag_user -d rag_db

-- Check document stats
SELECT 
    filename, 
    status, 
    chunk_count, 
    qa_pairs_count,
    vector_count
FROM documents
WHERE filename LIKE '%הפתוחה%'
ORDER BY created_at DESC;
```

## API Query (Advanced)

```bash
# Get chunks for a document
curl http://localhost:8000/documents/{document_id}/chunks

# Response will include type in metadata:
{
  "chunks": [
    {
      "id": "...",
      "content": "...",
      "metadata": {
        "type": "text_chunk"  // or "summary" or "qa"
      }
    }
  ]
}
```
