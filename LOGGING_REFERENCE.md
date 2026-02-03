# Hierarchical Summarization - Logging Reference

## Quick Reference for All Log Messages

This document lists all log messages emitted by the hierarchical summarizer for easy monitoring and debugging.

---

## Initialization Phase

### `HierarchicalSummarizer initialized`
**Level:** INFO  
**When:** Summarizer object is created  
**Data:**
- `deployment`: Azure OpenAI deployment name
- `short_doc_threshold`: Character threshold for single vs map-reduce
- `max_section_size`: Maximum section size in characters
- `max_concurrent_requests`: Parallel request limit

**Example:**
```json
{
  "level": "INFO",
  "message": "HierarchicalSummarizer initialized",
  "data": {
    "deployment": "gpt-4",
    "short_doc_threshold": 12000,
    "max_section_size": 15000,
    "max_concurrent_requests": 5
  }
}
```

---

## Document Processing Start

### `Starting hierarchical summarization`
**Level:** INFO  
**When:** Beginning of summarization for a document  
**Data:**
- `document_title`: Title of the document
- `document_type`: Type of document (PDF, DOCX, etc.)

### `Extracted document text`
**Level:** DEBUG  
**When:** After extracting full text from document tree  
**Data:**
- `text_length`: Total characters extracted
- `threshold`: Short document threshold for comparison

### `Using single summary method (short document)`
**Level:** INFO  
**When:** Document is small enough for single summary  
**Data:**
- `text_length`: Document length in characters

### `Using map-reduce method (long document)`
**Level:** INFO  
**When:** Document requires map-reduce approach  
**Data:**
- `text_length`: Document length in characters

---

## Single Summary Path

### `Starting short document summarization`
**Level:** INFO  
**When:** Beginning single summary generation  
**Data:**
- `document_title`: Document title
- `content_length`: Content length in characters

### `Generated short doc summary prompt`
**Level:** DEBUG  
**When:** Prompt created for short document  
**Data:**
- `prompt_length`: Total prompt length

### `Short document summarization complete`
**Level:** INFO  
**When:** Single summary generation finished  
**Data:**
- `document_title`: Document title
- `summary_length`: Generated summary length

---

## Map-Reduce Path - Phase 1: Splitting

### `Starting map-reduce summarization`
**Level:** INFO  
**When:** Beginning map-reduce process  
**Data:**
- `document_title`: Document title

### `MAP-REDUCE: Phase 1 - Splitting document into sections`
**Level:** INFO  
**When:** Starting document splitting phase  
**Data:** None

### `Starting document splitting`
**Level:** DEBUG  
**When:** Beginning split logic  
**Data:** None

### `Processing document children`
**Level:** DEBUG  
**When:** Examining document structure  
**Data:**
- `children_count`: Number of top-level nodes

### `Processing section`
**Level:** DEBUG  
**When:** Examining each section  
**Data:**
- `section_index`: Index of section (0-based)
- `section_title`: Title of section
- `section_length`: Section length in characters

### `Skipping short section`
**Level:** DEBUG  
**When:** Section is below minimum size  
**Data:**
- `section_title`: Section title
- `length`: Section length
- `min_size`: Minimum size threshold

### `Section too long, splitting into subsections`
**Level:** DEBUG  
**When:** Section exceeds maximum size  
**Data:**
- `section_title`: Original section title
- `length`: Section length
- `max_size`: Maximum size threshold

### `Splitting long section`
**Level:** DEBUG  
**When:** Beginning subsection creation  
**Data:**
- `title`: Section title
- `length`: Section length

### `Section has paragraphs`
**Level:** DEBUG  
**When:** Counting paragraphs in section  
**Data:**
- `title`: Section title
- `paragraph_count`: Number of paragraphs

### `Created subsection`
**Level:** DEBUG  
**When:** Subsection created  
**Data:**
- `title`: Subsection title (e.g., "Introduction (Part 1)")
- `length`: Subsection length
- `paragraphs_included`: Paragraph index

### `Created final subsection`
**Level:** DEBUG  
**When:** Last subsection created  
**Data:**
- `title`: Subsection title
- `length`: Subsection length

### `Long section split complete`
**Level:** INFO  
**When:** Finished splitting a long section  
**Data:**
- `original_title`: Original section title
- `parts_created`: Number of subsections

### `Section added`
**Level:** DEBUG  
**When:** Section added without splitting  
**Data:**
- `section_title`: Section title
- `length`: Section length

### `No structured sections found, using size-based splitting`
**Level:** WARNING  
**When:** No document structure detected  
**Data:** None

### `Starting size-based splitting`
**Level:** DEBUG  
**When:** Beginning fallback splitting  
**Data:**
- `text_length`: Total text length

### `Text split into paragraphs`
**Level:** DEBUG  
**When:** Paragraphs identified  
**Data:**
- `paragraph_count`: Number of paragraphs

### `Created size-based section`
**Level:** DEBUG  
**When:** Section created by size  
**Data:**
- `section_num`: Section number
- `length`: Section length

### `Created final size-based section`
**Level:** DEBUG  
**When:** Last size-based section created  
**Data:**
- `section_num`: Section number
- `length`: Section length

### `Size-based splitting complete`
**Level:** INFO  
**When:** Fallback splitting finished  
**Data:**
- `section_count`: Number of sections created

### `Document splitting complete`
**Level:** INFO  
**When:** All splitting finished  
**Data:**
- `total_sections`: Total sections created
- `total_chars`: Total characters across all sections

### `Document split into sections`
**Level:** INFO  
**When:** Summary of splitting results  
**Data:**
- `section_count`: Number of sections
- `avg_section_size`: Average section size

---

## Map-Reduce Path - Phase 2: MAP

### `MAP-REDUCE: Phase 2 - Summarizing sections in parallel`
**Level:** INFO  
**When:** Starting parallel summarization  
**Data:**
- `section_count`: Number of sections
- `max_concurrent`: Concurrency limit

### `Starting parallel section summarization`
**Level:** INFO  
**When:** Beginning MAP phase  
**Data:**
- `section_count`: Number of sections
- `max_concurrent`: Concurrency limit

### `Created summarization tasks`
**Level:** INFO  
**When:** All async tasks created  
**Data:**
- `task_count`: Number of tasks

### `Acquiring semaphore for section`
**Level:** DEBUG  
**When:** Section starts processing (gets semaphore)  
**Data:**
- `section_index`: Section index
- `section_title`: Section title

### `Summarizing section`
**Level:** INFO  
**When:** Beginning section summarization  
**Data:**
- `section_index`: Section index
- `section_title`: Section title
- `content_length`: Content length

### `Generated section summary prompt`
**Level:** DEBUG  
**When:** Prompt created for section  
**Data:**
- `section_index`: Section index
- `prompt_length`: Prompt length

### `Section summary complete`
**Level:** INFO  
**When:** Section summarization finished  
**Data:**
- `section_index`: Section index
- `section_title`: Section title
- `summary_length`: Summary length
- `compression_ratio`: Original/summary ratio

### `Released semaphore for section`
**Level:** DEBUG  
**When:** Section processing complete (releases semaphore)  
**Data:**
- `section_index`: Section index
- `section_title`: Section title

### `All section summarizations complete`
**Level:** INFO  
**When:** All sections summarized  
**Data:**
- `summaries_count`: Number of summaries

### `Section summaries complete`
**Level:** INFO  
**When:** MAP phase finished  
**Data:**
- `summaries_count`: Number of summaries
- `total_summary_length`: Combined summary length

---

## Map-Reduce Path - Phase 3: REDUCE

### `MAP-REDUCE: Phase 3 - Reducing to final summary`
**Level:** INFO  
**When:** Starting REDUCE phase  
**Data:** None

### `Starting reduce phase`
**Level:** INFO  
**When:** Beginning final summary creation  
**Data:**
- `document_title`: Document title
- `section_summaries_count`: Number of section summaries

### `Formatted section summaries`
**Level:** DEBUG  
**When:** Section summaries formatted for prompt  
**Data:**
- `formatted_length`: Length of formatted summaries

### `Generated final summary prompt`
**Level:** DEBUG  
**When:** Final summary prompt created  
**Data:**
- `prompt_length`: Prompt length

### `Reduce phase complete`
**Level:** INFO  
**When:** Final summary generated  
**Data:**
- `document_title`: Document title
- `final_summary_length`: Final summary length
- `original_total_length`: Total original content length
- `total_compression_ratio`: Overall compression ratio

### `Map-reduce summarization complete`
**Level:** INFO  
**When:** Entire map-reduce process finished  
**Data:**
- `document_title`: Document title
- `final_summary_length`: Final summary length
- `section_summaries_count`: Number of section summaries

---

## LLM API Calls

### `Starting LLM call`
**Level:** DEBUG  
**When:** Before making API call  
**Data:**
- `operation`: Operation identifier (e.g., "section_summary_0")
- `system_prompt_length`: System prompt length
- `user_prompt_length`: User prompt length
- `max_tokens`: Maximum tokens setting
- `temperature`: Temperature setting

### `LLM call successful`
**Level:** INFO  
**When:** API call completed successfully  
**Data:**
- `operation`: Operation identifier
- `prompt_tokens`: Input tokens used
- `completion_tokens`: Output tokens generated
- `total_tokens`: Total tokens
- `response_length`: Response length in characters

### `LLM call failed`
**Level:** ERROR  
**When:** API call failed  
**Data:**
- `operation`: Operation identifier
- `error`: Error message
- `error_type`: Exception class name

---

## Text Extraction

### `Extracting text from document tree`
**Level:** DEBUG  
**When:** Starting text extraction  
**Data:** None

### `Text extraction complete`
**Level:** DEBUG  
**When:** Text extraction finished  
**Data:**
- `extracted_length`: Length of extracted text
- `line_count`: Number of lines

---

## Consumer Integration

### `[4/8] Hierarchical summarization (Map-Reduce)`
**Level:** INFO  
**When:** Stage 4 of pipeline starts  
**Data:** None

### `Summarization complete: method=..., sections=..., summary_length=...`
**Level:** INFO  
**When:** Summarization stage complete  
**Data:** (in message string)
- `method`: 'single' or 'map_reduce'
- `sections`: Number of sections
- `summary_length`: Final summary length

---

## Monitoring Queries

### Find all summarization operations
```
level:"INFO" AND message:"hierarchical summarization"
```

### Track method distribution
```
message:"Summarization complete" | stats count by method
```

### Monitor token usage
```
message:"LLM call successful" | stats sum(total_tokens) by operation
```

### Track compression ratios
```
message:"Section summary complete" | avg(compression_ratio)
```

### Find errors
```
level:"ERROR" AND message:"LLM call failed"
```

### Monitor processing time
```
message:"Map-reduce summarization complete" | calculate duration
```

### Track parallel efficiency
```
message:"Acquiring semaphore" AND message:"Released semaphore"
| calculate avg_concurrent_requests
```

---

## Log Levels Summary

| Level | Count | Use Case |
|-------|-------|----------|
| DEBUG | 20 | Detailed step-by-step execution |
| INFO  | 18 | High-level progress and results |
| WARNING | 1 | Fallback to size-based splitting |
| ERROR | 1 | LLM API failures |

---

## Complete Log Flow Example

For a **long document (map-reduce)**:

```
INFO  | HierarchicalSummarizer initialized
INFO  | Starting hierarchical summarization
DEBUG | Extracted document text
INFO  | Using map-reduce method (long document)
INFO  | Starting map-reduce summarization
INFO  | MAP-REDUCE: Phase 1 - Splitting document into sections
DEBUG | Starting document splitting
DEBUG | Processing document children
DEBUG | Processing section (x6)
INFO  | Document splitting complete
INFO  | Document split into sections
INFO  | MAP-REDUCE: Phase 2 - Summarizing sections in parallel
INFO  | Starting parallel section summarization
INFO  | Created summarization tasks
DEBUG | Acquiring semaphore for section (x6)
INFO  | Summarizing section (x6)
DEBUG | Generated section summary prompt (x6)
DEBUG | Starting LLM call (x6)
INFO  | LLM call successful (x6)
INFO  | Section summary complete (x6)
DEBUG | Released semaphore for section (x6)
INFO  | All section summarizations complete
INFO  | Section summaries complete
INFO  | MAP-REDUCE: Phase 3 - Reducing to final summary
INFO  | Starting reduce phase
DEBUG | Formatted section summaries
DEBUG | Generated final summary prompt
DEBUG | Starting LLM call
INFO  | LLM call successful
INFO  | Reduce phase complete
INFO  | Map-reduce summarization complete
```

Total log messages: **~50 messages** for a 6-section document

---

## JSON Log Query Examples

### Elasticsearch/OpenSearch

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "worker": "ingestion" } },
        { "match": { "logger": "src.pipeline.summarizer" } }
      ],
      "filter": [
        { "range": { "timestamp": { "gte": "now-1h" } } }
      ]
    }
  },
  "aggs": {
    "methods": {
      "terms": { "field": "data.method" }
    },
    "avg_compression": {
      "avg": { "field": "data.compression_ratio" }
    }
  }
}
```

### Splunk

```
index=ingestion worker=ingestion logger=src.pipeline.summarizer
| stats count by data.method
| eval pct=round(count/sum(count)*100,2)
```

### CloudWatch Insights

```
fields @timestamp, message, data.method, data.total_tokens
| filter logger = "src.pipeline.summarizer"
| stats sum(data.total_tokens) by data.method
```
