// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const API_TIMEOUT = 30000; // 30 seconds

// File Upload
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
export const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'image/png',
  'image/jpeg',
  'image/tiff',
  '.pdf',
  '.docx',
  '.pptx',
  '.png',
  '.jpg',
  '.jpeg',
  '.tiff',
];

export const FILE_TYPE_LABELS: Record<string, string> = {
  'application/pdf': 'PDF',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
  'image/png': 'PNG',
  'image/jpeg': 'JPEG',
  'image/tiff': 'TIFF',
};

// Document Status
export const DOCUMENT_STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
};

export const DOCUMENT_STATUS_ICONS = {
  pending: '⏳',
  processing: '🔄',
  completed: '✅',
  failed: '❌',
};

// Service Status
export const SERVICE_STATUS_COLORS = {
  connected: 'text-green-600',
  degraded: 'text-yellow-600',
  disconnected: 'text-red-600',
};

export const SERVICE_STATUS_ICONS = {
  connected: '🟢',
  degraded: '🟡',
  disconnected: '🔴',
};

// Agent Decisions
export const AGENT_DECISION_COLORS = {
  proceed: 'bg-green-50 border-green-200',
  refine_query: 'bg-yellow-50 border-yellow-200',
  expand_search: 'bg-blue-50 border-blue-200',
};

export const AGENT_DECISION_LABELS = {
  proceed: '✅ PROCEED',
  refine_query: '🔄 REFINE QUERY',
  expand_search: '🔍 EXPAND SEARCH',
};

// Pagination
export const DEFAULT_PAGE_SIZE = 10;
export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

// Query Settings
export const DEFAULT_TOP_K = 10;
export const DEFAULT_RERANK_TOP = 5;
export const DEFAULT_MAX_ITERATIONS = 3;

// Chunk Types
export const CHUNK_TYPE_COLORS = {
  paragraph: 'bg-blue-50 border-blue-200',
  table: 'bg-purple-50 border-purple-200',
  image_description: 'bg-green-50 border-green-200',
  heading: 'bg-gray-50 border-gray-200',
};

export const CHUNK_TYPE_LABELS = {
  paragraph: 'Paragraph',
  table: 'Table',
  image_description: 'Image',
  heading: 'Heading',
};

// Chart Colors
export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#06b6d4',
};

// Timing Breakdown Colors (for charts)
export const TIMING_COLORS = {
  embedding_ms: '#3b82f6',
  search_ms: '#8b5cf6',
  rerank_ms: '#10b981',
  agent_ms: '#f59e0b',
  generation_ms: '#ef4444',
};

// Search Source Colors
export const SEARCH_SOURCE_COLORS = {
  vector_chunks: '#3b82f6',
  vector_summaries: '#8b5cf6',
  vector_qa: '#10b981',
  keyword_bm25: '#f59e0b',
};

// Debounce Delays
export const SEARCH_DEBOUNCE_MS = 300;
export const INPUT_DEBOUNCE_MS = 500;

// Toast Duration
export const TOAST_DURATION = 5000; // 5 seconds

// Refresh Intervals
export const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
export const DOCUMENT_LIST_REFRESH_INTERVAL = 10000; // 10 seconds
