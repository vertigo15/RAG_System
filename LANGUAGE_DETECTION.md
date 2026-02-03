# Language-Aware Document Processing

This RAG system now includes language detection at the chunk level, enabling language-specific retrieval and better multilingual support.

## Features

### 1. Word-Level Language Detection
Each word in a chunk is analyzed to determine its language using:
- **Character set detection** (fast, accurate for Hebrew/Arabic)
  - Hebrew: Unicode range `\u0590-\u05FF`
  - Arabic: Unicode range `\u0600-\u06FF`
  - Latin characters: Detected as English (or via Fasttext if available)
- **Fasttext model** (optional, for Latin-script language disambiguation)

### 2. Chunk-Level Language Metadata
Every chunk stored in Qdrant includes:
```json
{
    "doc_id": "123",
    "content": "שלום, my name is דוד",
    "language": "he",                    // Primary language
    "is_multilingual": true,             // Has multiple languages
    "languages": ["he", "en"],           // All detected languages
    "language_distribution": {           // Percentage breakdown
        "he": 0.4,
        "en": 0.6
    }
}
```

## Implementation

### Language Detector Module
Location: `workers/ingestion/src/pipeline/language_detector.py`

```python
from pipeline.language_detector import LanguageDetector

detector = LanguageDetector()

# Analyze text
result = detector.analyze_chunk_language("שלום my name is דוד")
print(result['primary_language'])      # 'en' (60% of words)
print(result['is_multilingual'])        # True
print(result['languages'])              # ['he', 'en']
print(result['distribution'])           # {'he': 0.4, 'en': 0.6}
```

### Integration Points

#### 1. Chunking Pipeline
`workers/ingestion/src/pipeline/chunker.py` automatically analyzes each chunk:
```python
for chunk in chunks:
    lang_info = self.language_detector.analyze_chunk_language(chunk['content'])
    chunk['language'] = lang_info['primary_language']
    chunk['is_multilingual'] = lang_info['is_multilingual']
    chunk['languages'] = lang_info['languages']
    chunk['language_distribution'] = lang_info['distribution']
```

#### 2. Qdrant Storage
`workers/ingestion/src/storage/qdrant_client.py` stores language metadata in the payload.

## Querying with Language Filters

### Example: Search Hebrew-only chunks
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = QdrantClient(host="localhost", port=6333)

results = client.search(
    collection_name="chunks",
    query_vector=embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="language",
                match=MatchValue(value="he")
            )
        ]
    )
)
```

### Example: Search multilingual chunks
```python
results = client.search(
    collection_name="chunks",
    query_vector=embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="is_multilingual",
                match=MatchValue(value=True)
            )
        ]
    )
)
```

### Example: Search chunks containing Hebrew
```python
results = client.search(
    collection_name="chunks",
    query_vector=embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="languages",
                match=MatchValue(any=["he"])
            )
        ]
    )
)
```

### Example: Exclude English chunks
```python
results = client.search(
    collection_name="chunks",
    query_vector=embedding,
    query_filter=Filter(
        must_not=[
            FieldCondition(
                key="language",
                match=MatchValue(value="en")
            )
        ]
    )
)
```

## Supported Languages

### Character-Based Detection (Built-in)
- **Hebrew** (`he`): Full support via Unicode character ranges
- **Arabic** (`ar`): Full support via Unicode character ranges
- **English** (`en`): Default for Latin characters

### Fasttext-Based Detection (Optional)
To enable advanced language detection for 176 languages:

1. Download the model:
   ```bash
   wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
   ```

2. Mount it in Docker:
   ```yaml
   # docker-compose.yml
   ingestion_worker:
     volumes:
       - ./models:/app/models
   ```

3. The system will automatically use it if available at `/app/models/lid.176.bin`

## Testing

Run the test script to verify language detection:
```bash
python test_language_detection.py
```

**Test cases:**
- Hebrew only: "שלום עולם זה טקסט בעברית"
- English only: "Hello world this is English text"
- Mixed: "שלום my name is דוד and I live in ירושלים"
- Arabic: "مرحبا بك في العالم العربي"

## Performance

- **Character-based detection**: ~0.1ms per word (no external dependencies)
- **Fasttext detection**: ~0.5ms per word (requires model download)
- **Chunk analysis**: ~10-50ms per chunk (500 tokens average)

## Future Enhancements

1. **Language-Specific Embeddings**: Use different embedding models per language
2. **Transliteration Detection**: Detect Hebrew/Arabic written in Latin script
3. **Code-Switching Analysis**: Identify language switching patterns
4. **Custom Language Models**: Fine-tune detection for domain-specific vocabulary

## Troubleshooting

### Fasttext not loading
If you see the warning: `Fasttext model not available, using character-based detection only`

This is **normal** and the system works fine without it. Character-based detection is sufficient for Hebrew/Arabic/English.

To enable Fasttext:
1. Install: `pip install fasttext-wheel`
2. Download model: `wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin`
3. Place at: `/app/models/lid.176.bin` (in Docker) or update `language_detector.py` path

### Incorrect language detection
- **Short chunks** (<10 words): May be less accurate
- **Mixed technical terms**: May be classified as English even if primary language is Hebrew
- **Solution**: Check `language_distribution` for actual percentages
