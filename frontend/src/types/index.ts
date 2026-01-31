export interface Document {
  id: string;
  filename: string;
  file_path: string;
  file_size: number;
  file_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count: number | null;
  error_message: string | null;
  uploaded_at: string;
  processed_at: string | null;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  text: string;
  type: 'text_chunk' | 'summary' | 'qa';
  section: string;
  score?: number;
  metadata: Record<string, any>;
}

export interface Query {
  id: string;
  query_text: string;
  document_ids: string[] | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  answer: string | null;
  citations: Citation[] | null;
  debug_data: DebugData | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
  updated_at: string;
}

export interface Citation {
  citation_number: number;
  text: string;
  section: string;
  document_id: string;
  type: string;
}

export interface DebugData {
  iterations: Iteration[];
  timing: Timing;
}

export interface Iteration {
  iteration_number: number;
  query_used: string;
  search_sources: SearchSources;
  chunks_before_rerank: ChunkSummary[];
  chunks_after_rerank: ChunkSummary[];
  agent_evaluation: AgentEvaluation;
  timing: IterationTiming;
}

export interface SearchSources {
  vector_chunks: number;
  vector_summaries: number;
  vector_qa: number;
  keyword_bm25: number;
  after_merge: number;
}

export interface ChunkSummary {
  id: string;
  score: number;
  text: string;
  section: string;
  rerank_position?: number;
}

export interface AgentEvaluation {
  decision: 'proceed' | 'refine_query' | 'expand_search';
  confidence: number;
  reasoning: string;
  refined_query: string | null;
}

export interface IterationTiming {
  embedding_ms: number;
  search_ms: number;
  rerank_ms: number;
  agent_ms: number;
  total_ms: number;
}

export interface Timing {
  embedding_ms: number;
  search_ms: number;
  rerank_ms: number;
  agent_ms: number;
  generation_ms: number;
  total_ms: number;
}

export interface Settings {
  azure_openai_endpoint: string;
  azure_openai_key: string;
  azure_openai_deployment_gpt4: string;
  azure_openai_deployment_embed: string;
  azure_doc_intelligence_endpoint: string;
  azure_doc_intelligence_key: string;
  chunk_size: number;
  chunk_overlap: number;
  retrieval_top_k: number;
  reranking_top_k: number;
  rrf_k: number;
  agent_max_iterations: number;
}

export interface HealthStatus {
  status: string;
  database: string;
  rabbitmq: string;
  qdrant: string;
}
