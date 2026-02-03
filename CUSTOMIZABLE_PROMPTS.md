# Customizable Prompts for Summary and Q&A Generation

The RAG system now supports customizable prompts for document summarization and Q&A generation, stored in the database settings table.

## What Was Added

### Database Settings
Two new settings have been added to the `settings` table:

1. **`prompt_summary`**: Template for generating document summaries
2. **`prompt_qa`**: Template for generating Q&A pairs

These are stored as JSON with `system` and `user` fields.

### Prompt Templates

#### Summary Prompt
```json
{
  "system": "You are an expert document analyst. Create a clear, accurate, and comprehensive summary of the provided document.",
  "user": "
## Guidelines
- Focus on main ideas, key findings, and important details
- Preserve critical numbers, dates, names, and statistics
- Be objective and factual - do not add interpretations
- If the document contains tables or data, highlight key insights

## Document Information
Title: {document_title}
Type: {document_type}

## Document Content
{document_content}

## Required Output Structure

### Overview
A 2-3 sentence high-level description of what this document is about.

### Key Points
The most important information (3-7 bullet points).

### Important Data
- Key numbers, statistics, percentages
- Important dates or deadlines
- Names of people, organizations, or products
- Specific requirements or conditions

### Conclusions
Main conclusions, recommendations, or action items (if present in the document).

Target length: 200-400 words. Write in the same language as the source document.
  "
}
```

#### Q&A Prompt
```json
{
  "system": "You are an expert at generating question-answer pairs for a document retrieval system.",
  "user": "
## Your Task
Analyze the document and generate {num_questions} diverse Q&A pairs that users would naturally ask.

## Guidelines
- Questions must be self-contained (understandable without context)
- Answers must be directly supported by the document - no assumptions
- Cover different sections and topics from the document
- Include diverse question types

## Question Types to Include
- **Factual**: Specific facts, numbers, dates, names (e.g., \"What was the revenue in Q3?\")
- **Overview**: General questions about purpose/topic (e.g., \"What is this document about?\")
- **Procedural**: How-to, processes, steps (e.g., \"How do I submit a request?\")
- **Comparison**: Comparing items, periods, options (e.g., \"How does X compare to Y?\")
- **Reasoning**: Why questions, causes, explanations (e.g., \"Why did sales increase?\")

## Document Information
Title: {document_title}
Type: {document_type}

## Document Content
{document_content}

## Required Output Format (JSON)
{
  \"qa_pairs\": [
    {
      \"question\": \"The question text\",
      \"answer\": \"The answer based on document content\",
      \"type\": \"factual|overview|procedural|comparison|reasoning\"
    }
  ]
}

Generate questions in the same language as the source document.
  "
}
```

## How It Works

### 1. Database Storage
Prompts are stored in the `settings` table during initialization:
```sql
INSERT INTO settings (key, value, description) VALUES
    ('prompt_summary', '{"system": "...", "user": "..."}', 'Prompt template for document summarization'),
    ('prompt_qa', '{"system": "...", "user": "..."}', 'Prompt template for Q&A generation')
ON CONFLICT (key) DO NOTHING;
```

### 2. Runtime Loading
When processing a document, the enrichment module:
1. Connects to PostgreSQL
2. Loads `prompt_summary` and `prompt_qa` from settings
3. Uses these prompts for LLM API calls

### 3. Template Variables
Prompts support placeholders that are replaced at runtime:

**Summary prompt:**
- `{document_title}`: Document filename
- `{document_type}`: File type (PDF, DOCX, TXT, etc.)
- `{document_content}`: Extracted text content

**Q&A prompt:**
- `{num_questions}`: Number of Q&A pairs to generate (default: 5)
- `{document_title}`: Document filename
- `{document_type}`: File type
- `{document_content}`: Extracted text content

## Implementation Files

### Modified Files
1. **`init-db.sql`**: Added prompt settings
2. **`workers/ingestion/src/pipeline/enrichment.py`**: 
   - Load prompts from database
   - Use custom prompts for LLM calls
   - Parse JSON Q&A responses
3. **`workers/ingestion/src/storage/postgres_client.py`**:
   - Added `get_setting()` method
4. **`workers/ingestion/src/consumer.py`**:
   - Pass postgres_storage to Enrichment

## Customizing Prompts

### Via Database
```sql
-- Update summary prompt
UPDATE settings
SET value = '{"system": "Custom system prompt", "user": "Custom user prompt with {document_content}"}'
WHERE key = 'prompt_summary';

-- Update Q&A prompt
UPDATE settings
SET value = '{"system": "Custom system prompt", "user": "Custom user prompt with {num_questions} questions"}'
WHERE key = 'prompt_qa';
```

### Via Settings UI (Future)
The settings can be edited through the Settings page in the UI.

## Benefits

### 1. Flexibility
- Change prompts without rebuilding code
- A/B test different prompt strategies
- Adapt to specific document types or industries

### 2. Multilingual Support
Prompts instruct LLM to "Write in the same language as the source document", enabling:
- Hebrew summaries for Hebrew documents
- English summaries for English documents
- Mixed-language handling

### 3. Structured Output
Q&A prompt requests JSON output with:
- `question`: The question text
- `answer`: The answer from document
- `type`: Question category (factual, overview, procedural, comparison, reasoning)

This enables:
- Better chunk metadata
- Question-type filtering in retrieval
- Analytics on question distribution

## Example Output

### Summary Chunk
```json
{
  "chunk_id": "summary_doc",
  "text": "### Overview\nThis document outlines the Q3 2023 financial results...\n\n### Key Points\n- Revenue increased 25% to $2.5M\n- Customer count grew from 150 to 200\n- New product launched in September\n\n### Important Data\n- Q3 Revenue: $2.5M (up from $2.0M in Q2)\n- Gross margin: 68%\n- Churn rate: 3.2%\n\n### Conclusions\nStrong growth trajectory continues. Recommend increased investment in sales.",
  "type": "summary",
  "language": "en"
}
```

### Q&A Chunk
```json
{
  "chunk_id": "qa_3",
  "text": "Q: What was the revenue in Q3 2023?\nA: The revenue in Q3 2023 was $2.5M, representing a 25% increase from the previous quarter.",
  "type": "qa",
  "metadata": {
    "question": "What was the revenue in Q3 2023?",
    "answer": "The revenue in Q3 2023 was $2.5M, representing a 25% increase from the previous quarter.",
    "question_type": "factual"
  }
}
```

## Fallback Behavior

If prompts fail to load from the database:
- System uses default hardcoded prompts
- Warning logged but processing continues
- No interruption to document ingestion

## Token Usage

Updated limits to accommodate richer prompts:
- **Summary**: 600 tokens max (was 200)
- **Q&A**: 1000 tokens max (was 500)
- **Q&A pairs**: 5 pairs default (was 3)

## Future Enhancements

### 1. Per-Document-Type Prompts
```sql
INSERT INTO settings VALUES
  ('prompt_summary_pdf', '...'),
  ('prompt_summary_json', '...'),
  ('prompt_qa_legal', '...');
```

### 2. Prompt Versioning
```sql
ALTER TABLE settings ADD COLUMN version INTEGER;
```

### 3. Prompt Templates Library
Pre-defined prompts for:
- Legal documents
- Financial reports
- Technical documentation
- Medical records

### 4. Prompt Analytics
Track which prompts produce:
- Best retrieval performance
- Highest user satisfaction
- Most diverse Q&A pairs

## Troubleshooting

### Prompts Not Loading
**Problem**: Enrichment uses default prompts

**Solution**: Check database contains the settings:
```sql
SELECT key, value FROM settings WHERE key LIKE 'prompt_%';
```

### Invalid JSON in Prompt
**Problem**: Error during prompt formatting

**Solution**: Validate JSON structure:
```sql
SELECT key, jsonb_typeof(value) FROM settings WHERE key = 'prompt_summary';
```

### Missing Template Variables
**Problem**: Prompt has `{document_content}` but error occurs

**Solution**: Ensure all placeholders match exactly (case-sensitive)

### Q&A Not Parsing
**Problem**: Q&A pairs returned but not stored

**Solution**: Check logs for JSON parsing errors. LLM should return:
```json
{"qa_pairs": [...]}
```

## Summary

**Status**: ✅ Complete and deployed

**Features**:
- Customizable prompts stored in database
- Template variable substitution
- JSON-based Q&A output
- Multilingual support
- Fallback to defaults if needed

**Next steps**:
1. Upload documents to test new prompts
2. Verify summaries follow new format
3. Check Q&A pairs have question types
4. Customize prompts for specific use cases
