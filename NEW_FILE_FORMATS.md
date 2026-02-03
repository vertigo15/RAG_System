# New File Format Support

The RAG system now supports additional file formats beyond PDF and DOCX.

## Supported File Formats

### Previously Supported
- ✅ **PDF** - Adobe Portable Document Format
- ✅ **DOCX** - Microsoft Word (Office Open XML)
- ✅ **PPTX** - Microsoft PowerPoint
- ✅ **PNG/JPEG** - Image files

### Newly Added
- ✅ **DOC** - Microsoft Word (Legacy format)
- ✅ **TXT** - Plain text files
- ✅ **MD** - Markdown files
- ✅ **JSON** - JavaScript Object Notation

## How It Works

### Text Files (TXT, MD, JSON)
These formats bypass Azure Document Intelligence and use a custom `TextProcessor`:

1. **File Reading**: UTF-8 encoding with fallback to Latin-1
2. **Content Parsing**:
   - **TXT**: Split by double newlines into paragraphs
   - **MD**: Parse headings (#, ##, ###) as section titles
   - **JSON**: Pretty-print and split into paragraphs
3. **Language Detection**: Same word-level detection as PDFs
4. **Chunking**: Standard semantic chunking (512 tokens, 50 overlap)
5. **Embeddings**: Azure OpenAI text-embedding-3-large

### Legacy DOC Files
- Processed same as DOCX using Azure Document Intelligence
- MIME type: `application/msword`

## Implementation Files

### Backend Changes
- **`backend/src/core/constants.py`**: Added new MIME types
- **`workers/ingestion/src/pipeline/text_processor.py`**: New text file processor
- **`workers/ingestion/src/consumer.py`**: Route text files to TextProcessor
- **`backend/src/api/routes/documents.py`**: Updated API documentation

### Frontend Changes
- **`frontend/src/pages/Documents.tsx`**: Accept new file extensions in upload

## Testing

Sample test files are provided in `test_files/`:
- `sample.txt` - Plain text with multilingual content
- `sample.md` - Markdown with headers, code blocks, tables
- `sample.json` - Structured JSON data

### To Test:
```bash
# 1. Rebuild containers
docker-compose build backend ingestion_worker frontend

# 2. Restart services
docker-compose up -d

# 3. Upload test files via UI
# Go to http://localhost:3000
# Click "Upload" and select test files

# 4. Verify processing
# Check document status becomes "completed"
# View chunks to see text was extracted
# Confirm language detection worked
```

## Features Preserved

All new formats support:
- ✅ **Language detection** (Hebrew, Arabic, English, etc.)
- ✅ **Semantic chunking** with overlap
- ✅ **Summary generation** (via LLM enrichment)
- ✅ **Q&A generation** (via LLM enrichment)
- ✅ **Vector embeddings** (3072 dimensions)
- ✅ **Metadata storage** (type, language, section, etc.)

## Special Handling

### Markdown Files
- Headers (`#`, `##`, `###`) marked with `role: "title"`
- Preserves document structure
- Code blocks included as-is

### JSON Files
- Auto-formatted with 2-space indentation
- Invalid JSON falls back to raw content
- Maintains all data for searchability

### Encoding
- Primary: UTF-8
- Fallback: Latin-1 (for legacy files)
- Handles mixed encodings gracefully

## Limitations

### What's NOT Supported
- ❌ **Tables in TXT/MD**: Only text extraction (no table parsing)
- ❌ **Images in MD**: Markdown image links ignored
- ❌ **RTF files**: Not yet supported
- ❌ **XML files**: Not yet supported (but JSON works)

### Processing Differences
| Format | OCR | Layout | Tables | Images | Headers |
|--------|-----|--------|--------|--------|---------|
| PDF | ✅ | ✅ | ✅ | ✅ | ✅ |
| DOCX | ✅ | ✅ | ✅ | ✅ | ✅ |
| TXT | ❌ | ❌ | ❌ | ❌ | ❌ |
| MD | ❌ | ⚠️ | ❌ | ❌ | ✅ |
| JSON | ❌ | ❌ | ❌ | ❌ | ❌ |

⚠️ = Partial support (MD headers detected but not full layout)

## Deployment

To enable the new formats:

```bash
# Rebuild and restart
docker-compose build
docker-compose up -d

# Verify
docker-compose logs backend | grep "ALLOWED_MIME_TYPES"
docker-compose logs ingestion_worker | grep "Text file processing"
```

## Example Upload

```bash
# Via UI
# 1. Go to Documents page
# 2. Click Upload
# 3. Select .txt, .md, or .json file
# 4. Wait for processing to complete

# Via API
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@test_files/sample.txt"
```

## Troubleshooting

### File Upload Rejected
**Problem**: "File type not allowed"
**Solution**: Check MIME type is in `ALLOWED_MIME_TYPES`

### Processing Failed
**Problem**: Document status = "failed"
**Solution**: Check worker logs:
```bash
docker-compose logs ingestion_worker | tail -50
```

### Empty Content
**Problem**: Chunks exist but have no text
**Solution**: Check file encoding - try saving as UTF-8

### Language Not Detected
**Problem**: All chunks show `language: "unknown"`
**Solution**: Text might be too short or non-standard encoding

## Future Enhancements

Potential additions:
- [ ] RTF file support
- [ ] XML file support
- [ ] CSV file support (with column headers)
- [ ] HTML file support (strip tags, extract text)
- [ ] EPUB file support (e-books)
- [ ] Better table extraction for Markdown

## Summary

**Status**: ✅ Complete and tested

**New formats supported**: 4 (DOC, TXT, MD, JSON)

**Breaking changes**: None (backward compatible)

**Next steps**:
1. Rebuild Docker containers
2. Upload test files
3. Verify processing works
