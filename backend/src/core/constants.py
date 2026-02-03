"""
System-wide constants.
"""

# Queue names
INGESTION_QUEUE = "ingestion_queue"
QUERY_QUEUE = "query_queue"

# Qdrant collections
CHUNKS_COLLECTION = "documents_chunks"
SUMMARIES_COLLECTION = "documents_summaries"
QA_COLLECTION = "documents_qa"

# Embedding size for text-embedding-3-large
EMBEDDING_SIZE = 3072

# File upload
MAX_FILE_SIZE_MB = 100
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/msword",  # .doc
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    "image/png",
    "image/jpeg",
    "text/plain",  # .txt
    "text/markdown",  # .md
    "application/json",  # .json
    "application/octet-stream"  # Fallback for files with unknown MIME type
]

# Processing
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 10
DEFAULT_RERANK_TOP = 5
MAX_AGENT_ITERATIONS = 3

# RRF parameters
RRF_K = 60
