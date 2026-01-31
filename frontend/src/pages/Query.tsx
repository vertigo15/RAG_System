import { useState, useEffect } from 'react';
import { useSubmitQuery } from '../hooks/useApi';
import { queriesApi } from '../services/api';
import { Send, Loader2, Clock, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { Query as QueryType, Iteration } from '../types';

export default function Query() {
  const [queryText, setQueryText] = useState('');
  const [currentQuery, setCurrentQuery] = useState<QueryType | null>(null);
  const submitQuery = useSubmitQuery();
  
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (currentQuery && (currentQuery.status === 'pending' || currentQuery.status === 'processing')) {
      interval = setInterval(async () => {
        const { data } = await queriesApi.getById(currentQuery.id);
        setCurrentQuery(data);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [currentQuery?.id, currentQuery?.status]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryText.trim()) return;
    const result = await submitQuery.mutateAsync({ query_text: queryText });
    setCurrentQuery(result);
  };
  
  const isProcessing = currentQuery?.status === 'pending' || currentQuery?.status === 'processing';
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Query & Debug</h1>
      
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={submitQuery.isPending || isProcessing}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold px-6 py-3 rounded-lg flex items-center gap-2 disabled:opacity-50"
          >
            {isProcessing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            Query
          </button>
        </div>
      </form>
      
      {currentQuery && (
        <div className="space-y-6">
          <AnswerDisplay query={currentQuery} />
          {currentQuery.debug_data && <DebugPanel debugData={currentQuery.debug_data} />}
        </div>
      )}
    </div>
  );
}

function AnswerDisplay({ query }: { query: QueryType }) {
  if (query.status === 'processing' || query.status === 'pending') {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-3">
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          <span className="text-lg">Processing your query...</span>
        </div>
      </div>
    );
  }
  
  if (query.status === 'failed') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-red-800 mb-2">Error</h2>
        <p className="text-red-600">{query.error_message}</p>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Answer</h2>
      <p className="text-gray-800 mb-6 whitespace-pre-wrap">{query.answer}</p>
      
      {query.citations && query.citations.length > 0 && (
        <div>
          <h3 className="font-semibold text-lg mb-3">Citations</h3>
          <div className="space-y-3">
            {query.citations.map((citation) => (
              <div key={citation.citation_number} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="text-sm font-semibold text-blue-600">[{citation.citation_number}] {citation.section}</div>
                <p className="text-sm text-gray-600 mt-1">{citation.text.substring(0, 200)}...</p>
                <div className="text-xs text-gray-400 mt-1">{citation.type}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DebugPanel({ debugData }: { debugData: any }) {
  const [selectedIteration, setSelectedIteration] = useState(0);
  const iteration = debugData.iterations[selectedIteration];
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Debug Information</h2>
      
      {/* Timing Summary */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
        <TimingStat label="Embedding" value={debugData.timing.embedding_ms} />
        <TimingStat label="Search" value={debugData.timing.search_ms} />
        <TimingStat label="Rerank" value={debugData.timing.rerank_ms} />
        <TimingStat label="Agent" value={debugData.timing.agent_ms} />
        <TimingStat label="Generation" value={debugData.timing.generation_ms} />
        <TimingStat label="Total" value={debugData.timing.total_ms} highlight />
      </div>
      
      {/* Iteration Selector */}
      <div className="flex gap-2 mb-6">
        {debugData.iterations.map((it: Iteration, idx: number) => (
          <button
            key={idx}
            onClick={() => setSelectedIteration(idx)}
            className={`px-4 py-2 rounded-lg font-semibold ${
              selectedIteration === idx
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Iteration {it.iteration_number}
          </button>
        ))}
      </div>
      
      {iteration && (
        <div className="space-y-6">
          {/* Query Used */}
          <div>
            <h3 className="font-semibold text-lg mb-2">Query Used</h3>
            <p className="bg-gray-50 p-3 rounded-lg text-sm">{iteration.query_used}</p>
          </div>
          
          {/* Search Sources Chart */}
          <div>
            <h3 className="font-semibold text-lg mb-2">Search Sources Distribution</h3>
            <div className="flex items-center">
              <div className="w-64 h-64">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Vector Chunks', value: iteration.search_sources.vector_chunks },
                        { name: 'Vector Summaries', value: iteration.search_sources.vector_summaries },
                        { name: 'Vector Q&A', value: iteration.search_sources.vector_qa },
                        { name: 'Keyword (BM25)', value: iteration.search_sources.keyword_bm25 },
                      ]}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      label
                    >
                      <Cell fill="#3B82F6" />
                      <Cell fill="#10B981" />
                      <Cell fill="#F59E0B" />
                      <Cell fill="#EF4444" />
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="ml-6 text-sm space-y-2">
                <div><span className="font-semibold">After Merge:</span> {iteration.search_sources.after_merge} chunks</div>
              </div>
            </div>
          </div>
          
          {/* Chunks Before/After Rerank */}
          <div className="grid grid-cols-2 gap-4">
            <ChunkList title="Before Rerank" chunks={iteration.chunks_before_rerank} />
            <ChunkList title="After Rerank" chunks={iteration.chunks_after_rerank} />
          </div>
          
          {/* Agent Evaluation */}
          <div>
            <h3 className="font-semibold text-lg mb-2">Agent Evaluation</h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <div><span className="font-semibold">Decision:</span> <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">{iteration.agent_evaluation.decision}</span></div>
              <div><span className="font-semibold">Confidence:</span> {(iteration.agent_evaluation.confidence * 100).toFixed(1)}%</div>
              <div><span className="font-semibold">Reasoning:</span> {iteration.agent_evaluation.reasoning}</div>
              {iteration.agent_evaluation.refined_query && (
                <div><span className="font-semibold">Refined Query:</span> {iteration.agent_evaluation.refined_query}</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function TimingStat({ label, value, highlight = false }: any) {
  return (
    <div className={`p-3 rounded-lg ${highlight ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50'}`}>
      <div className="flex items-center gap-2 mb-1">
        <Clock className="w-4 h-4 text-gray-500" />
        <span className="text-xs font-medium text-gray-600">{label}</span>
      </div>
      <div className={`text-lg font-bold ${highlight ? 'text-blue-600' : 'text-gray-800'}`}>{value}ms</div>
    </div>
  );
}

function ChunkList({ title, chunks }: any) {
  return (
    <div>
      <h4 className="font-semibold mb-2">{title}</h4>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {chunks.map((chunk: any, idx: number) => (
          <div key={idx} className="text-xs bg-gray-50 p-2 rounded border">
            <div className="font-semibold text-gray-700">{chunk.section}</div>
            <div className="text-gray-600 mt-1 line-clamp-2">{chunk.text}</div>
            <div className="text-gray-400 mt-1 flex justify-between">
              <span>Score: {chunk.score.toFixed(4)}</span>
              {chunk.rerank_position && <span>Rank: #{chunk.rerank_position}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
