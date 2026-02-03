import { FC } from 'react';
import { X, RotateCcw, Trash2, Eye } from 'lucide-react';
import { Document } from '../../types';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Card } from '../common/Card';
import {
  formatFileSize,
  formatDate,
  formatProcessingTime,
  truncateText,
} from '../../utils/formatters';

interface DocumentDetailPanelProps {
  document: Document | null;
  onClose: () => void;
  onDelete: (id: string) => void;
  onReprocess?: (id: string) => void;
  onViewChunks?: (id: string) => void;
  isDeleting?: boolean;
}

export const DocumentDetailPanel: FC<DocumentDetailPanelProps> = ({
  document,
  onClose,
  onDelete,
  onReprocess,
  onViewChunks,
  isDeleting,
}) => {
  if (!document) return null;

  const statusVariantMap: Record<string, any> = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'danger',
  };

  const handleDelete = () => {
    if (window.confirm(`Delete "${document.filename}"? This cannot be undone.`)) {
      onDelete(document.id);
    }
  };

  return (
    <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white border-l border-gray-200 shadow-lg overflow-y-auto z-40">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900">📋 Document Details</h2>
        <button
          onClick={onClose}
          className="p-1 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="p-6 space-y-6">
        {/* File Name */}
        <div>
          <h3 className="font-semibold text-gray-900 break-words">
            {document.filename}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            {document.mime_type || 'Unknown type'}
          </p>
        </div>

        {/* Status Badge */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">Status</p>
          <Badge variant={statusVariantMap[document.status]}>
            {document.status.charAt(0).toUpperCase() +
              document.status.slice(1)}
          </Badge>
          {document.error_message && (
            <p className="text-xs text-red-600 mt-2">{document.error_message}</p>
          )}
        </div>

        {/* Metadata Cards */}
        <Card className="bg-gray-50">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-gray-600 uppercase">
                File Size
              </p>
              <p className="text-sm font-semibold text-gray-900 mt-1">
                {formatFileSize(document.file_size_bytes)}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-600 uppercase">
                Chunks
              </p>
              <p className="text-sm font-semibold text-gray-900 mt-1">
                {document.chunk_count || 0}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-600 uppercase">
                Vectors
              </p>
              <p className="text-sm font-semibold text-gray-900 mt-1">
                {document.vector_count || 0}
              </p>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-600 uppercase">
                Q&A Pairs
              </p>
              <p className="text-sm font-semibold text-gray-900 mt-1">
                {document.qa_pairs_count || 0}
              </p>
            </div>
          </div>
        </Card>

        {/* Processing Time */}
        {document.processing_time_seconds !== null && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">
              Processing Time
            </p>
            <p className="text-sm text-gray-900 font-semibold">
              {formatProcessingTime(document.processing_time_seconds)}
            </p>
          </div>
        )}

        {/* Languages */}
        {document.detected_languages && document.detected_languages.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Languages</p>
            <div className="flex flex-wrap gap-2">
              {document.detected_languages.map((lang, idx) => (
            <Badge key={idx} variant="info">
                  {lang}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {document.tags && document.tags.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Tags</p>
            <div className="flex flex-wrap gap-2">
              {document.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        {document.summary && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Summary</p>
            <div className="bg-gray-50 rounded-md p-3">
              <p className="text-sm text-gray-700 leading-relaxed">
                {truncateText(document.summary, 300)}
              </p>
            </div>
          </div>
        )}

        {/* Upload Info */}
        <Card className="bg-gray-50">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Uploaded</span>
              <span className="text-gray-900 font-medium">
                {formatDate(document.uploaded_at)}
              </span>
            </div>
            {document.processing_completed_at && (
              <div className="flex justify-between">
                <span className="text-gray-600">Processed</span>
                <span className="text-gray-900 font-medium">
                  {formatDate(document.processing_completed_at)}
                </span>
              </div>
            )}
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="space-y-2 pt-4 border-t border-gray-200">
          {onViewChunks && document.chunk_count > 0 && (
            <Button
              fullWidth
              variant="secondary"
              size="sm"
              icon={<Eye className="h-4 w-4" />}
              onClick={() => onViewChunks(document.id)}
            >
              👁 View Chunks
            </Button>
          )}
          {onReprocess && document.status !== 'processing' && (
            <Button
              fullWidth
              variant="secondary"
              size="sm"
              icon={<RotateCcw className="h-4 w-4" />}
              onClick={() => onReprocess(document.id)}
            >
              🔄 Reprocess
            </Button>
          )}
          <Button
            fullWidth
            variant="danger"
            size="sm"
            icon={<Trash2 className="h-4 w-4" />}
            onClick={handleDelete}
            disabled={isDeleting}
          >
            🗑️ Delete
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetailPanel;
