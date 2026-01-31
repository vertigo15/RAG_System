# RAG System - Production-Ready Retrieval Augmented Generation

A production-grade RAG system built with Docker microservices, Azure OpenAI, and PostgreSQL. Features include agentic query processing, hybrid search, document intelligence, and a full admin UI.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Frontend │  │ Backend  │  │ Ingestion│  │  Query   │       │
│  │  (React) │  │  (API)   │  │  Worker  │  │  Worker  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┼─────────────┼─────────────┘              │
│                     │             │                            │
│              ┌──────┴──────┐  ┌───┴────┐                       │
│              │  RabbitMQ   │  │ Qdrant │                       │
│              └─────────────┘  └────────┘                       │
│                                                                 │
│              ┌─────────────┐                                   │
│              │  PostgreSQL │                                   │
│              └─────────────┘                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────────────┐
              │        Azure Cloud Services           │
              │  ┌───────────┐  ┌────────────────┐   │
              │  │  OpenAI   │  │   Document     │   │
              │  │  Service  │  │  Intelligence  │   │
              │  └───────────┘  └────────────────┘   │
              └───────────────────────────────────────┘
```

## Features

### Core Capabilities
- **Document Ingestion**: 7-stage pipeline (OCR, Vision, Tree Building, Enrichment, Chunking, Embeddings, Storage)
- **Agentic Query Processing**: Iterative query refinement with up to 3 iterations
- **Hybrid Search**: RRF-based fusion of vector and keyword search
- **Admin UI**: React-based interface for document management and debugging

### Production Features
- ✅ JSON structured logging with request/correlation ID tracking
- ✅ PostgreSQL-based rate limiting (no Redis dependency)
- ✅ Global error handling with consistent JSON responses
- ✅ Health checks for all services
- ✅ Async/await throughout for performance
- ✅ Type hints and Pydantic validation
- ✅ Dockerized deployment

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Azure OpenAI subscription
- Azure Document Intelligence subscription

### Setup

1. **Clone and configure**
   ```bash
   git clone <repository>
   cd RAG_System
   cp .env.example .env
   ```

2. **Edit `.env` with your Azure credentials**
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_key_here
   AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_DOC_INTELLIGENCE_KEY=your_key_here
   POSTGRES_USER=rag_user
   POSTGRES_PASSWORD=your_secure_password
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672 (guest/guest)
   - Qdrant Dashboard: http://localhost:6333/dashboard

## Project Structure

```
RAG_System/
├── docker-compose.yml
├── .env.example
├── init-db.sql
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── config.py                    # Pydantic settings
│   │   ├── main.py                      # FastAPI app
│   │   ├── dependencies.py              # DI container
│   │   │
│   │   ├── core/
│   │   │   ├── logging.py               # JSON structured logging
│   │   │   ├── exceptions.py            # Custom exceptions
│   │   │   └── constants.py             # System constants
│   │   │
│   │   ├── models/
│   │   │   ├── database.py              # SQLAlchemy models
│   │   │   ├── schemas.py               # Pydantic schemas
│   │   │   └── enums.py                 # Status enums
│   │   │
│   │   ├── api/
│   │   │   ├── middleware/
│   │   │   │   ├── logging.py           # Request/response logging
│   │   │   │   ├── rate_limit.py        # PostgreSQL rate limiter
│   │   │   │   └── error_handler.py     # Global error handler
│   │   │   │
│   │   │   └── routes/
│   │   │       ├── health.py            # Health checks
│   │   │       ├── documents.py         # Document endpoints
│   │   │       ├── queries.py           # Query endpoints
│   │   │       └── settings.py          # Settings endpoints
│   │   │
│   │   ├── repositories/
│   │   │   ├── document_repository.py   # Document CRUD
│   │   │   ├── query_repository.py      # Query CRUD
│   │   │   └── settings_repository.py   # Settings CRUD
│   │   │
│   │   └── services/
│   │       ├── document_service.py      # Document business logic
│   │       ├── query_service.py         # Query business logic
│   │       ├── queue_service.py         # RabbitMQ operations
│   │       └── settings_service.py      # Settings management
│   │
│   └── tests/
│
├── workers/
│   ├── ingestion/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── main.py                  # Worker entry point
│   │   │   ├── config.py                # Worker config
│   │   │   ├── consumer.py              # RabbitMQ consumer
│   │   │   │
│   │   │   ├── pipeline/
│   │   │   │   ├── document_intelligence.py  # Azure Document Intelligence
│   │   │   │   ├── vision_processor.py       # GPT-4 Vision
│   │   │   │   ├── tree_builder.py           # Document tree
│   │   │   │   ├── enrichment.py             # Summary & Q&A
│   │   │   │   ├── chunker.py                # Semantic chunking
│   │   │   │   └── embedder.py               # Embedding generation
│   │   │   │
│   │   │   └── storage/
│   │   │       ├── qdrant_client.py     # Vector storage
│   │   │       └── postgres_client.py   # Metadata storage
│   │
│   └── query/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── src/
│       │   ├── main.py
│       │   ├── config.py
│       │   ├── consumer.py
│       │   │
│       │   ├── pipeline/
│       │   │   ├── embedder.py          # Query embedding
│       │   │   ├── retriever.py         # Hybrid search
│       │   │   ├── reranker.py          # Result reranking
│       │   │   ├── agent.py             # Agentic evaluation
│       │   │   └── generator.py         # Answer generation
│       │   │
│       │   └── storage/
│       │       └── qdrant_client.py     # RRF hybrid search
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── src/
    │   ├── App.tsx
    │   │
    │   ├── pages/
    │   │   ├── Settings.tsx             # Azure config & RAG settings
    │   │   ├── Documents.tsx            # Document management
    │   │   └── Query.tsx                # Query & debug interface
    │   │
    │   ├── components/
    │   │   ├── DocumentUpload.tsx
    │   │   ├── DocumentList.tsx
    │   │   ├── DocumentDetails.tsx
    │   │   ├── ChunksViewer.tsx
    │   │   ├── AnswerDisplay.tsx
    │   │   └── DebugPanel.tsx           # Iteration debug info
    │   │
    │   ├── hooks/
    │   │   ├── useDocuments.ts
    │   │   └── useQuery.ts
    │   │
    │   ├── services/
    │   │   └── api.ts                   # Axios API client
    │   │
    │   └── types/
    │       └── index.ts
```

## API Endpoints

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get document details
- `GET /documents/{id}/chunks` - Get document chunks
- `DELETE /documents/{id}` - Delete document

### Queries
- `POST /queries` - Submit query
- `GET /queries/{id}` - Get query result

### Settings
- `GET /settings` - Get current settings
- `PUT /settings` - Update settings

### Health
- `GET /health` - Overall health status

## Ingestion Pipeline

The document ingestion pipeline consists of 7 stages:

1. **Azure Document Intelligence**: Extract document structure (pages, paragraphs, tables, images)
2. **Vision Processing**: OCR and semantic description of images using GPT-4 Vision
3. **Tree Building**: Build unified document tree merging text and image descriptions
4. **Enrichment**: Generate document summary and Q&A pairs using Azure OpenAI LLM
5. **Semantic Chunking**: Language-aware chunking respecting sentence boundaries
6. **Embedding Generation**: Generate embeddings using text-embedding-3-large
7. **Storage**: Store chunks, summaries, Q&A in Qdrant and update PostgreSQL metadata

## Query Pipeline

The agentic query pipeline:

1. **Embed Query**: Generate query embedding
2. **Hybrid Search**: RRF-based fusion of vector and keyword search
3. **Rerank**: Rerank results using cross-encoder or LLM
4. **Agent Evaluation**: Evaluate context sufficiency
   - PROCEED: Generate answer
   - REFINE_QUERY: Modify query and retry
   - EXPAND_SEARCH: Broaden search and retry
5. **Generation**: Generate answer with citations

Maximum 3 iterations with full debug tracking.

## Environment Variables

See `.env.example` for all configuration options.

### Required
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service endpoint
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_DOC_INTELLIGENCE_ENDPOINT` - Azure Document Intelligence endpoint
- `AZURE_DOC_INTELLIGENCE_KEY` - Azure Document Intelligence API key
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password

### Optional (with defaults)
- `AZURE_EMBEDDING_DEPLOYMENT` - Embedding model (default: text-embedding-3-large)
- `AZURE_LLM_DEPLOYMENT` - LLM model (default: gpt-4)
- `DEFAULT_TOP_K` - Initial retrieval count (default: 10)
- `DEFAULT_RERANK_TOP` - Post-rerank count (default: 5)
- `MAX_AGENT_ITERATIONS` - Max query iterations (default: 3)
- `CHUNK_SIZE` - Chunk size in tokens (default: 512)
- `CHUNK_OVERLAP` - Chunk overlap (default: 50)
- `RATE_LIMIT_PER_MINUTE` - Rate limit (default: 60)

## Development

### Running locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

**Ingestion Worker:**
```bash
cd workers/ingestion
pip install -r requirements.txt
python src/main.py
```

**Query Worker:**
```bash
cd workers/query
pip install -r requirements.txt
python src/main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

### Testing
```bash
cd backend
pytest tests/
```

## Troubleshooting

### Services won't start
- Check Docker is running: `docker info`
- Check logs: `docker-compose logs -f <service-name>`
- Verify .env file has all required variables

### Connection errors
- Ensure all services are healthy: `docker-compose ps`
- Check service health: `curl http://localhost:8000/health`
- Verify network connectivity between containers

### Rate limiting
- Rate limits are per IP address or API key
- Current limits: 60 requests/minute, 1000 requests/hour
- Adjust in .env: `RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_PER_HOUR`

## Monitoring

### Logs
All services use JSON structured logging:
```bash
docker-compose logs -f backend
docker-compose logs -f ingestion-worker
docker-compose logs -f query-worker
```

### Metrics
- Request IDs track requests across services
- Correlation IDs trace distributed workflows
- Response time headers on all API responses

## Contributing

This is a production-ready template. Customize as needed:
1. Add authentication/authorization
2. Implement backup/restore procedures
3. Add monitoring (Prometheus, Grafana)
4. Set up CI/CD pipelines
5. Configure SSL/TLS
6. Add distributed tracing

## License

MIT License - See LICENSE file for details

## Status

**Current Implementation:**
- ✅ Infrastructure (Docker Compose, PostgreSQL, Qdrant, RabbitMQ)
- ✅ Core utilities (Logging, Exceptions, Configuration)
- ✅ Database models and schemas
- ✅ Middleware stack (Logging, Rate Limiting, Error Handling)
- 🚧 Repository layer (In Progress)
- 🚧 Service layer (In Progress)
- 🚧 API routes (In Progress)
- 📋 Workers (Pending)
- 📋 Frontend (Pending)

**Next Steps:**
1. Complete backend API (repositories, services, routes)
2. Implement ingestion worker pipeline
3. Implement query worker pipeline
4. Build React frontend
5. End-to-end testing
