import { FC, useEffect, useState } from 'react';
import { X, FileText, Database, Search } from 'lucide-react';
import { Button } from '../common/Button';
import { api } from '../../services/api';

interface Chunk {
  id: string;
  content: string;
  doc_id: string;
  hierarchy_path?: string;
  score?: number;
  metadata: Record<string, any>;
}

interface ChunksViewerModalProps {
  documentId: string;
  documentName: string;
  onClose: () => void;
}

export const ChunksViewerModal: FC<ChunksViewerModalProps> = ({
  documentId,
  documentName,
  onClose,
}) => {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChunk, setSelectedChunk] = useState<Chunk | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredChunks, setFilteredChunks] = useState<Chunk[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('all');

  useEffect(() => {
    fetchChunks();
  }, [documentId]);

  useEffect(() => {
    let filtered = chunks;
    
    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(
        (chunk) => (chunk.metadata?.type || 'text_chunk') === typeFilter
      );
    }
    
    // Filter by search query
    if (searchQuery.trim() !== '') {
      // Wildcard search - convert * to regex .* and escape special chars
      const searchPattern = searchQuery
        .toLowerCase()
        .replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape special regex chars
        .replace(/\\\*/g, '.*'); // Convert * to .*
      
      const regex = new RegExp(searchPattern, 'i');
      
      filtered = filtered.filter(
        (chunk) =>
          regex.test(chunk.content) ||
          regex.test(chunk.hierarchy_path || '') ||
          regex.test(chunk.metadata?.type || '')
      );
    }
    
    setFilteredChunks(filtered);
  }, [searchQuery, typeFilter, chunks]);

  const fetchChunks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/documents/${documentId}/chunks`);
      const loadedChunks = response.data.chunks || [];
      setChunks(loadedChunks);
      setFilteredChunks(loadedChunks);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load chunks');
    } finally {
      setLoading(false);
    }
  };

  const getChunkTypeLabel = (type: string) => {
    switch (type) {
      case 'text_chunk':
        return 'Text';
      case 'summary':
        return 'Summary';
      case 'qa':
        return 'Q&A';
      default:
        return type;
    }
  };

  const getChunkTypeColor = (type: string) => {
    switch (type) {
      case 'text_chunk':
        return 'bg-blue-100 text-blue-800';
      case 'summary':
        return 'bg-green-100 text-green-800';
      case 'qa':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Database className="h-6 w-6 text-blue-600" />
              Document Chunks
            </h2>
            <p className="text-sm text-gray-600 mt-1">{documentName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {/* Search Bar and Filters */}
          <div className="px-4 py-3 border-b border-gray-200 bg-white space-y-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search chunks... (use * for wildcard)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
            
            {/* Type Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-600">Type:</span>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setTypeFilter('all')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    typeFilter === 'all'
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All ({chunks.length})
                </button>
                <button
                  onClick={() => setTypeFilter('text_chunk')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    typeFilter === 'text_chunk'
                      ? 'bg-blue-600 text-white'
                      : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                  }`}
                >
                  Text ({chunks.filter(c => (c.metadata?.type || 'text_chunk') === 'text_chunk').length})
                </button>
                <button
                  onClick={() => setTypeFilter('summary')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    typeFilter === 'summary'
                      ? 'bg-green-600 text-white'
                      : 'bg-green-100 text-green-800 hover:bg-green-200'
                  }`}
                >
                  Summaries ({chunks.filter(c => c.metadata?.type === 'summary').length})
                </button>
                <button
                  onClick={() => setTypeFilter('qa')}
                  className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                    typeFilter === 'qa'
                      ? 'bg-purple-600 text-white'
                      : 'bg-purple-100 text-purple-800 hover:bg-purple-200'
                  }`}
                >
                  Q&A ({chunks.filter(c => c.metadata?.type === 'qa').length})
                </button>
              </div>
            </div>
            
            {(searchQuery || typeFilter !== 'all') && (
              <p className="text-xs text-gray-600">
                Showing {filteredChunks.length} of {chunks.length} chunks
              </p>
            )}
          </div>

          <div className="flex-1 overflow-hidden flex">
            {/* Chunk List */}
            <div className="w-1/3 border-r border-gray-200 overflow-y-auto bg-gray-50">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Loading chunks...</p>
                </div>
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-full p-6">
                <div className="text-center">
                  <p className="text-red-600">{error}</p>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={fetchChunks}
                    className="mt-4"
                  >
                    Retry
                  </Button>
                </div>
              </div>
            ) : filteredChunks.length === 0 ? (
              <div className="flex items-center justify-center h-full p-6">
                <div className="text-center text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>{searchQuery ? 'No matching chunks found' : 'No chunks found'}</p>
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="text-sm text-blue-600 hover:text-blue-700 mt-2"
                    >
                      Clear search
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="p-4 space-y-2">
                <div className="text-sm text-gray-600 mb-4 font-medium">
                  {filteredChunks.length} chunk{filteredChunks.length !== 1 ? 's' : ''}
                  {searchQuery && ` (${chunks.length} total)`}
                </div>
                {filteredChunks.map((chunk, index) => (
                  <button
                    key={chunk.id}
                    onClick={() => setSelectedChunk(chunk)}
                    className={`w-full text-left p-3 rounded-lg border transition-all ${
                      selectedChunk?.id === chunk.id
                        ? 'bg-blue-50 border-blue-300 shadow-sm'
                        : 'bg-white border-gray-200 hover:border-blue-200 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-xs font-semibold text-gray-500">
                        Chunk #{index + 1}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium ${getChunkTypeColor(
                          chunk.metadata?.type || 'text_chunk'
                        )}`}
                      >
                        {getChunkTypeLabel(chunk.metadata?.type || 'text_chunk')}
                      </span>
                    </div>
                    {chunk.hierarchy_path && (
                      <p className="text-xs text-gray-600 mb-1 truncate">
                        📁 {chunk.hierarchy_path}
                      </p>
                    )}
                    <p className="text-sm text-gray-700 line-clamp-2">
                      {chunk.content}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Chunk Detail */}
          <div className="flex-1 overflow-y-auto p-6">
            {selectedChunk ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Chunk Details
                  </h3>
                  <span
                    className={`text-sm px-3 py-1 rounded-full font-medium ${getChunkTypeColor(
                      selectedChunk.metadata?.type || 'text_chunk'
                    )}`}
                  >
                    {getChunkTypeLabel(selectedChunk.metadata?.type || 'text_chunk')}
                  </span>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <div>
                    <label className="text-xs font-medium text-gray-600 uppercase">
                      Chunk ID
                    </label>
                    <p className="text-sm text-gray-900 font-mono mt-1">
                      {selectedChunk.id}
                    </p>
                  </div>

                  {selectedChunk.hierarchy_path && (
                    <div>
                      <label className="text-xs font-medium text-gray-600 uppercase">
                        Section
                      </label>
                      <p className="text-sm text-gray-900 mt-1">
                        {selectedChunk.hierarchy_path}
                      </p>
                    </div>
                  )}

                  {selectedChunk.metadata && Object.keys(selectedChunk.metadata).length > 0 && (
                    <div>
                      <label className="text-xs font-medium text-gray-600 uppercase">
                        Metadata
                      </label>
                      <div className="mt-1 bg-white rounded border border-gray-200 p-2">
                        <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                          {JSON.stringify(selectedChunk.metadata, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-600 uppercase mb-2 block">
                    Content
                  </label>
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">
                      {selectedChunk.content}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <div className="text-center">
                  <FileText className="h-16 w-16 mx-auto mb-4 opacity-30" />
                  <p className="text-lg">Select a chunk to view details</p>
                </div>
              </div>
            )}
          </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChunksViewerModal;
