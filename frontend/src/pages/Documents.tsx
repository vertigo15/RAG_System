import { useState } from 'react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Table } from '../components/common/Table';
import { Badge } from '../components/common/Badge';
import { ProgressBar } from '../components/common/ProgressBar';
import { DocumentDetailPanel } from '../components/documents/DocumentDetailPanel';
import { ChunksViewerModal } from '../components/documents/ChunksViewerModal';
import { useDocuments } from '../hooks/useDocuments';
import { Spinner } from '../components/common/Spinner';
import { Upload, Search, RotateCcw } from 'lucide-react';
import {
  formatDate,
  formatFileSize,
  formatProcessingTime,
  calculateDocumentProgress,
} from '../utils/formatters';
import { Document } from '../types';

export default function Documents() {
  const {
    documents,
    isLoading,
    uploadDocument,
    deleteDocument,
    isUploading,
    isDeleting,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    page,
    setPage,
    totalPages,
    total,
    refetch,
  } = useDocuments();

  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [detailPanelOpen, setDetailPanelOpen] = useState(false);
  const [chunksModalOpen, setChunksModalOpen] = useState(false);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadDocument(e.target.files);
    }
  };

  const handleRowClick = (document: Document) => {
    // If clicking on already-selected document, open chunks viewer
    if (selectedDocument?.id === document.id && detailPanelOpen) {
      setChunksModalOpen(true);
    } else {
      // Otherwise, open detail panel
      setSelectedDocument(document);
      setDetailPanelOpen(true);
    }
  };

  const handleCloseDetail = () => {
    setDetailPanelOpen(false);
    setTimeout(() => setSelectedDocument(null), 300);
  };

  const handleDeleteDocument = (id: string) => {
    deleteDocument(id);
    setDetailPanelOpen(false);
    setTimeout(() => setSelectedDocument(null), 500);
  };

  const handleViewChunks = () => {
    setChunksModalOpen(true);
  };

  const columns = [
    {
      key: 'filename',
      title: 'Name',
      render: (value: string, row: Document) => (
        <div
          className="font-medium text-gray-900 cursor-pointer hover:text-blue-600 truncate"
          onClick={() => handleRowClick(row)}
        >
          📄 {value}
        </div>
      ),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value: string, row: Document) => {
        const variantMap: Record<string, any> = {
          pending: 'warning',
          processing: 'info',
          completed: 'success',
          failed: 'danger',
        };

        const progress = calculateDocumentProgress(
          value,
          row.chunk_count,
          row.vector_count
        );

        return (
          <div className="space-y-1">
            <Badge variant={variantMap[value]}>{value}</Badge>
            {value === 'processing' && (
              <ProgressBar
                progress={progress}
                variant="info"
                size="sm"
                className="max-w-[120px]"
              />
            )}
          </div>
        );
      },
    },
    {
      key: 'processing_time_seconds',
      title: 'Time',
      render: (value: number | null) => formatProcessingTime(value),
    },
    {
      key: 'vector_count',
      title: 'Vectors',
      render: (value: number) => value || '-',
    },
    {
      key: 'chunk_count',
      title: 'Chunks',
      render: (value: number) => value || '-',
    },
    {
      key: 'file_size_bytes',
      title: 'Size',
      render: (value: number) => formatFileSize(value),
    },
    {
      key: 'uploaded_at',
      title: 'Uploaded',
      render: (value: string) => formatDate(value),
    },
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className={`max-w-7xl mx-auto px-6 space-y-6 ${detailPanelOpen ? 'pr-[408px]' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">📄 Documents</h1>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            icon={<RotateCcw className="h-4 w-4" />}
            onClick={() => refetch()}
            disabled={isLoading}
          >
            Refresh
          </Button>
          <input
            type="file"
            id="file-upload"
            multiple
            accept=".pdf,.doc,.docx,.pptx,.png,.jpg,.jpeg,.tiff,.txt,.md,.json"
            onChange={handleUpload}
            className="hidden"
            disabled={isUploading}
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {isUploading ? (
                <Spinner size="sm" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              Upload
            </span>
          </label>
        </div>
      </div>

      {/* Search and Filter */}
      <Card>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents by name, tags, or summary..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter || ''}
              onChange={(e) => setStatusFilter(e.target.value || null)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          {/* Document Count */}
          <div className="text-sm text-gray-600">
            Total: <span className="font-semibold text-gray-900">{total}</span> documents
            {searchQuery && ` (${documents.length} filtered)`}
          </div>
        </div>
      </Card>

      {/* Documents Table */}
      <Card>
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No documents found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <Table
                columns={columns}
                data={documents}
                keyExtractor={(row: Document) => row.id}
                emptyMessage="No documents uploaded yet"
              />
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-4 flex items-center justify-between border-t border-gray-200 pt-4">
                <div className="text-sm text-gray-600">
                  Page <span className="font-semibold">{page}</span> of{' '}
                  <span className="font-semibold">{totalPages}</span>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                  >
                    ◀ Previous
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => setPage(page + 1)}
                    disabled={page === totalPages}
                  >
                    Next ▶
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>

      {/* Detail Panel */}
      {detailPanelOpen && (
        <DocumentDetailPanel
          document={selectedDocument}
          onClose={handleCloseDetail}
          onDelete={handleDeleteDocument}
          onViewChunks={handleViewChunks}
          isDeleting={isDeleting}
        />
      )}

      {/* Chunks Viewer Modal */}
      {chunksModalOpen && selectedDocument && (
        <ChunksViewerModal
          documentId={selectedDocument.id}
          documentName={selectedDocument.filename}
          onClose={() => setChunksModalOpen(false)}
        />
      )}
    </div>
  );
}
