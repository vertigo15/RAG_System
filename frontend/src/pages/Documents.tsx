import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Table } from '../components/common/Table';
import { Badge } from '../components/common/Badge';
import { useDocuments } from '../hooks/useDocuments';
import { Spinner } from '../components/common/Spinner';
import { Upload, Trash2 } from 'lucide-react';
import { formatDate, formatFileSize } from '../utils/formatters';
import { Document } from '../types';

export default function Documents() {
  const { documents, isLoading, uploadDocument, deleteDocument, isUploading } = useDocuments();

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadDocument(e.target.files);
    }
  };

  const columns = [
    {
      key: 'filename',
      title: 'Name',
      render: (value: string) => (
        <div className="font-medium text-gray-900">📄 {value}</div>
      ),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value: string) => {
        const variantMap: Record<string, any> = {
          pending: 'warning',
          processing: 'info',
          completed: 'success',
          failed: 'danger',
        };
        return <Badge variant={variantMap[value]}>{value}</Badge>;
      },
    },
    {
      key: 'uploaded_at',
      title: 'Uploaded',
      render: (value: string) => formatDate(value),
    },
    {
      key: 'file_size',
      title: 'Size',
      render: (value: number) => formatFileSize(value),
    },
    {
      key: 'chunk_count',
      title: 'Chunks',
      render: (value: number | null) => value || '-',
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, row: Document) => (
        <Button
          size="sm"
          variant="danger"
          onClick={(e) => {
            e.stopPropagation();
            if (window.confirm('Delete this document?')) {
              deleteDocument(row.id);
            }
          }}
          icon={<Trash2 className="h-4 w-4" />}
        >
          Delete
        </Button>
      ),
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
    <div className="max-w-7xl mx-auto px-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">📄 Documents</h1>
        <div>
          <input
            type="file"
            id="file-upload"
            multiple
            accept=".pdf,.docx,.pptx,.png,.jpg,.jpeg,.tiff"
            onChange={handleUpload}
            className="hidden"
            disabled={isUploading}
          />
          <label htmlFor="file-upload">
            <Button
              as="span"
              loading={isUploading}
              icon={<Upload className="h-4 w-4" />}
            >
              Upload Documents
            </Button>
          </label>
        </div>
      </div>

      <Card>
        <div className="mb-4 text-sm text-gray-600">
          Total: {documents.length} documents
        </div>
        <Table
          columns={columns}
          data={documents}
          keyExtractor={(row: Document) => row.id}
          emptyMessage="No documents uploaded yet"
        />
      </Card>
    </div>
  );
}
