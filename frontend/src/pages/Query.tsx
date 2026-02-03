import { useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Textarea } from '../components/common/Input';
import { Spinner } from '../components/common/Spinner';
import { Badge } from '../components/common/Badge';
import { useQuerySubmit } from '../hooks/useQueryHook';
import { Search } from 'lucide-react';
import { formatDuration, formatConfidence } from '../utils/formatters';

export default function Query() {
  const [query, setQuery] = useState('');
  const [debugMode, setDebugMode] = useState(false);
  const { submitQuery, result, isLoading } = useQuerySubmit();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      submitQuery({
        query_text: query,
        debug_mode: debugMode,
        document_filter: undefined,
      });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">🔍 Query & Debug</h1>

      {/* Query Input */}
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Textarea
            label="Enter your question"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="What were the revenue numbers for Q3?"
            rows={4}
          />
          
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={debugMode}
                onChange={(e) => setDebugMode(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-700">Enable Debug Mode</span>
            </label>
          </div>

          <Button
            type="submit"
            loading={isLoading}
            disabled={!query.trim()}
            icon={<Search className="h-4 w-4" />}
          >
            Ask Question
          </Button>
        </form>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card>
          <div className="flex flex-col items-center justify-center py-12">
            <Spinner size="lg" />
            <p className="mt-4 text-gray-600">Processing your query...</p>
          </div>
        </Card>
      )}

      {/* Answer */}
      {result && !isLoading && (
        <>
          <Card title="💬 Answer">
            <div className="prose max-w-none">
              <p className="text-gray-900 whitespace-pre-wrap">{result.answer}</p>
            </div>

            {result.citations && result.citations.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">📎 Sources:</h4>
                <div className="space-y-2">
                  {result.citations.map((citation, idx) => (
                    <div
                      key={idx}
                      className="text-sm text-gray-600 bg-gray-50 p-3 rounded"
                    >
                      [{idx + 1}] {citation.document_name}
                      {citation.section && ` - ${citation.section}`}
                      {citation.page_number && ` (Page ${citation.page_number})`}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-6 flex gap-4">
              <Badge variant="info">
                Confidence: {formatConfidence(result.confidence_score || 0)}
              </Badge>
              <Badge variant="default">
                Response Time: {formatDuration(result.total_time_ms || 0)}
              </Badge>
              <Badge variant="default">
                Iterations: {result.iteration_count || 1}
              </Badge>
            </div>
          </Card>

          {/* Debug Panel */}
          {debugMode && result.debug_data && (
            <Card title="🔧 Debug Panel">
              <div className="space-y-4">
                {result.debug_data.iterations?.map((iteration, idx) => (
                  <div key={idx} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Iteration {iteration.iteration_number}
                    </h4>
                    
                    <div className="space-y-3 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Query: </span>
                        <span className="text-gray-600">{iteration.query_used}</span>
                      </div>

                      {iteration.search_sources && (
                        <div>
                          <span className="font-medium text-gray-700">Search Sources: </span>
                          <div className="flex gap-2 mt-1">
                            <Badge size="sm" variant="info">
                              Vector: {iteration.search_sources.vector_chunks}
                            </Badge>
                            <Badge size="sm" variant="success">
                              BM25: {iteration.search_sources.keyword_bm25}
                            </Badge>
                            <Badge size="sm" variant="default">
                              Merged: {iteration.search_sources.after_merge}
                            </Badge>
                          </div>
                        </div>
                      )}

                      {iteration.agent_evaluation && (
                        <div>
                          <span className="font-medium text-gray-700">Agent Decision: </span>
                          <Badge
                            variant={
                              iteration.agent_evaluation.decision === 'proceed'
                                ? 'success'
                                : 'warning'
                            }
                          >
                            {iteration.agent_evaluation.decision.toUpperCase()}
                          </Badge>
                          <p className="text-gray-600 mt-1">
                            {iteration.agent_evaluation.reasoning}
                          </p>
                        </div>
                      )}

                      <div>
                        <span className="font-medium text-gray-700">Duration: </span>
                        <span className="text-gray-600">
                          {formatDuration(iteration.timing?.total_ms || 0)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
