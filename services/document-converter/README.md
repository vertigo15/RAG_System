# Document Converter Service

A dedicated service that converts various document formats (PDF, DOCX, TXT, MD, XLSX) to markdown and stores them in MinIO for the RAG pipeline.

## Overview

This service is the first step in the RAG document processing pipeline:

```
[Backend API] → [RabbitMQ: ingestion_queue] → [Document Converter] → [MinIO: markdown/] → [RabbitMQ: chunking_queue] → [Chunking Service]
```

## Features

- **Multi-format support**: PDF, DOCX, TXT, MD, XLSX
- **Azure Document Intelligence**: OCR and structure extraction for PDFs
- **Image descriptions**: GPT-4o vision for charts, diagrams, and images
- **Table extraction**: Preserves table structure in markdown
- **Table summaries**: GPT-4o summaries for large Excel sheets
- **Encoding detection**: Automatic text encoding detection for TXT files
- **MinIO storage**: Stores converted markdown for downstream processing

## Architecture

### Components

1. **Converters** (`src/converters/`)
   - `base.py`: Abstract base converter
   - `pdf_converter.py`: PDF → Markdown using Azure Document Intelligence
   - `text_converter.py`: TXT → Markdown with encoding detection
   - `markdown_converter.py`: MD passthrough
   - `docx_converter.py`: DOCX → Markdown (TODO: full implementation)
   - `excel_converter.py`: XLSX → Markdown with table summaries (TODO: full implementation)

2. **Services** (`src/services/`)
   - `minio_service.py`: MinIO upload operations
   - `vision_service.py`: GPT-4o vision for image descriptions
   - `llm_service.py`: GPT-4o for table summaries

3. **Utils** (`src/utils/`)
   - `encoding.py`: Text encoding detection
   - `markdown_helpers.py`: Markdown formatting utilities

4. **Router** (`src/router.py`)
   - Routes files to appropriate converters based on extension

5. **Main Worker** (`src/main.py`)
   - RabbitMQ consumer
   - Orchestrates conversion pipeline
   - Publishes to chunking queue

## Configuration

All configuration is via environment variables (see `.env`):

### Required
- `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database credentials
- `RABBITMQ_USER`, `RABBITMQ_PASSWORD`: Message queue credentials
- `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`: Object storage credentials
- `AZURE_DOC_INTELLIGENCE_ENDPOINT`, `AZURE_DOC_INTELLIGENCE_KEY`: Document Intelligence API
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`: OpenAI API
- `AZURE_LLM_DEPLOYMENT`: GPT-4 deployment name

### Optional
- `ENABLE_IMAGE_DESCRIPTIONS`: Enable/disable image descriptions (default: true)
- `ENABLE_TABLE_SUMMARIES`: Enable/disable table summaries (default: true)
- `MAX_FILE_SIZE_MB`: Maximum file size (default: 100)
- `TABLE_SUMMARY_THRESHOLD_ROWS`: Rows threshold for summaries (default: 50)

## Message Formats

### Input (from ingestion_queue)
```json
{
  "document_id": "uuid",
  "file_path": "/app/uploads/document.pdf",
  "original_filename": "document.pdf",
  "mime_type": "application/pdf",
  "correlation_id": "..."
}
```

### Output (to chunking_queue)
```json
{
  "doc_id": "uuid",
  "markdown_path": "markdown/uuid.md",
  "original_filename": "document.pdf",
  "file_type": "pdf",
  "image_count": 3,
  "table_count": 5
}
```

## MinIO Structure

```
documents/
├── markdown/
│   └── {document_id}.md       # Converted markdown
└── images/                     # Optional: extracted images
    └── {document_id}/
        └── {image_id}.png
```

## Development

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (copy `.env.example` to `.env`)

3. Run locally:
```bash
python -m src.main
```

### Adding a New Converter

1. Create converter in `src/converters/`:
```python
from converters.base import BaseConverter

class MyConverter(BaseConverter):
    def get_file_type(self) -> str:
        return "ext"
    
    def convert(self, file_bytes, filename, document_id=None):
        # Implementation
        pass
```

2. Register in `src/main.py`:
```python
self.converters = {
    'ext': MyConverter(...)
}
```

## Docker

### Build
```bash
docker build -t document-converter services/document-converter/
```

### Run with Docker Compose
```bash
docker-compose up document-converter
```

## Testing

1. Place test files in `test_files/`
2. Upload via backend API
3. Monitor logs:
```bash
docker-compose logs -f document-converter
```

## Monitoring

- **Logs**: JSON structured logging with levels
- **Metrics**: Processing time per document in ConversionResult
- **Errors**: Failed conversions logged with stack traces

## Performance

- **PDF (10 pages)**: ~30-60 seconds (Azure Doc Intelligence)
- **Text files**: <1 second
- **Excel (large)**: ~10-30 seconds (with summaries)
- **Bottlenecks**: Azure Document Intelligence, GPT-4o vision

## Troubleshooting

### "Unsupported file type"
- Check file extension is supported
- Add converter for new file types

### "Failed to upload markdown"
- Verify MinIO credentials
- Check MinIO service is running
- Ensure bucket exists

### "Document Intelligence timeout"
- Increase `doc_intelligence_timeout` setting
- Check Azure service status
- Verify API key and endpoint

### "Rate limit errors"
- Reduce concurrent processing
- Check Azure OpenAI quota
- Implement retry with backoff

## TODO

1. Complete DOCX converter implementation (images, formatting)
2. Complete Excel converter implementation
3. Add PostgreSQL status updates
4. Implement image extraction for PDFs
5. Add unit tests for all converters
6. Add integration tests with RabbitMQ and MinIO

## License

Part of the RAG System project.
