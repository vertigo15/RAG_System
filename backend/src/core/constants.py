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
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image/png",
    "image/jpeg",
    "text/plain"
]

# Processing
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 10
DEFAULT_RERANK_TOP = 5
MAX_AGENT_ITERATIONS = 3

# RRF parameters
RRF_K = 60
