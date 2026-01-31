-- RAG System Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_started_at TIMESTAMP WITH TIME ZONE,
    processing_completed_at TIMESTAMP WITH TIME ZONE,
    processing_time_seconds FLOAT,
    chunk_count INTEGER DEFAULT 0,
    vector_count INTEGER DEFAULT 0,
    qa_pairs_count INTEGER DEFAULT 0,
    detected_languages TEXT[],
    summary TEXT,
    tags TEXT[],
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Queries table
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    answer TEXT,
    confidence_score FLOAT,
    citations JSONB,
    total_time_ms INTEGER,
    iteration_count INTEGER,
    debug_data JSONB,
    document_filter UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table (key-value store)
CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rate limits table
CREATE TABLE rate_limits (
    key VARCHAR(255) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    request_count INTEGER DEFAULT 1,
    PRIMARY KEY (key, window_start)
);

-- Indexes for performance
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX idx_documents_filename ON documents(filename);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX idx_rate_limits_key_time ON rate_limits(key, window_start DESC);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default settings
INSERT INTO settings (key, value, description) VALUES
    ('azure_openai_endpoint', '""', 'Azure OpenAI service endpoint'),
    ('azure_openai_api_key', '""', 'Azure OpenAI API key'),
    ('azure_embedding_deployment', '"text-embedding-3-large"', 'Azure OpenAI embedding model deployment name'),
    ('azure_llm_deployment', '"gpt-4"', 'Azure OpenAI LLM deployment name'),
    ('azure_doc_intelligence_endpoint', '""', 'Azure Document Intelligence endpoint'),
    ('azure_doc_intelligence_key', '""', 'Azure Document Intelligence API key'),
    ('default_top_k', '10', 'Default number of chunks to retrieve'),
    ('default_rerank_top', '5', 'Default number of chunks after reranking'),
    ('max_agent_iterations', '3', 'Maximum agent iterations for query refinement'),
    ('chunk_size', '512', 'Default chunk size in tokens'),
    ('chunk_overlap', '50', 'Default chunk overlap in tokens')
ON CONFLICT (key) DO NOTHING;

-- Cleanup function for old rate limit records
CREATE OR REPLACE FUNCTION cleanup_old_rate_limits()
RETURNS void AS $$
BEGIN
    DELETE FROM rate_limits WHERE window_start < NOW() - INTERVAL '2 hours';
END;
$$ LANGUAGE plpgsql;
