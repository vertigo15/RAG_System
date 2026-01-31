import { useState } from 'react';
import { useDocuments, useUploadDocument, useDeleteDocument, useDocument, useDocumentChunks } from '../hooks/useApi';
import { Upload, File, Trash2, Eye, X, Loader2 } from 'lucide-react';
import type { Document } from '../types';

export default function Documents() {
  const { data: documents, isLoading } = useDocuments();
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [showChunks, setShowChunks] = useState<string | null>(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Documents</h1>
        <button
          onClick={() => setUploadModalOpen(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg flex items-center gap-2"
        >
          <Upload className="w-5 h-5" />
          Upload Document
        </button>
      </div>
      
      {isLoading ? (
        <div className="flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>
      ) : (
        <DocumentList documents={documents || []} onView={setSelectedDoc} onViewChunks={setShowChunks} />
      )}
      
      {uploadModalOpen && <UploadModal onClose={() => setUploadModalOpen(false)} />}
      {selectedDoc && <DocumentDetailsModal docId={selectedDoc} onClose={() => setSelectedDoc(null)} />}
      {showChunks && <ChunksViewerModal docId={showChunks} onClose={() => setShowChunks(null)} />}
    </div>
  );
}

function DocumentList({ documents, onView, onViewChunks }: any) {
  const deleteDoc = useDeleteDocument();
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Filename</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chunks</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {documents.map((doc: Document) => (
            <tr key={doc.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <File className="w-5 h-5 text-gray-400 mr-2" />
                  <span className="font-medium">{doc.filename}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(doc.status)}`}>
                  {doc.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {doc.chunk_count ? (
                  <button onClick={() => onViewChunks(doc.id)} className="text-blue-500 hover:underline">
                    {doc.chunk_count} chunks
                  </button>
                ) : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(doc.uploaded_at).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                <button onClick={() => onView(doc.id)} className="text-blue-500 hover:text-blue-700 mr-3">
                  <Eye className="w-5 h-5" />
                </button>
                <button 
                  onClick={() => deleteDoc.mutate(doc.id)} 
                  className="text-red-500 hover:text-red-700"
                  disabled={deleteDoc.isPending}
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function UploadModal({ onClose }: any) {
  const upload = useUploadDocument();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };
  
  const handleUpload = async () => {
    if (file) {
      await upload.mutateAsync(file);
      onClose();
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Upload Document</h2>
          <button onClick={onClose}><X className="w-6 h-6" /></button>
        </div>
        
        <div
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
        >
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-sm text-gray-600 mb-2">Drag and drop file here, or click to select</p>
          <input
            type="file"
            onChange={(e) => e.target.files && setFile(e.target.files[0])}
            className="hidden"
            id="fileInput"
          />
          <label htmlFor="fileInput" className="text-blue-500 hover:underline cursor-pointer">
            Browse files
          </label>
          {file && <p className="mt-4 text-sm font-medium">{file.name}</p>}
        </div>
        
        <button
          onClick={handleUpload}
          disabled={!file || upload.isPending}
          className="w-full mt-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg disabled:opacity-50"
        >
          {upload.isPending ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : 'Upload'}
        </button>
      </div>
    </div>
  );
}

function DocumentDetailsModal({ docId, onClose }: any) {
  const { data: doc } = useDocument(docId);
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Document Details</h2>
          <button onClick={onClose}><X className="w-6 h-6" /></button>
        </div>
        
        {doc && (
          <div className="space-y-3">
            <Field label="Filename" value={doc.filename} />
            <Field label="Status" value={doc.status} />
            <Field label="File Size" value={`${(doc.file_size / 1024).toFixed(2)} KB`} />
            <Field label="File Type" value={doc.file_type} />
            <Field label="Chunks" value={doc.chunk_count?.toString() || '-'} />
            <Field label="Uploaded" value={new Date(doc.uploaded_at).toLocaleString()} />
            {doc.processed_at && <Field label="Processed" value={new Date(doc.processed_at).toLocaleString()} />}
            {doc.error_message && <Field label="Error" value={doc.error_message} className="text-red-600" />}
          </div>
        )}
      </div>
    </div>
  );
}

function ChunksViewerModal({ docId, onClose }: any) {
  const { data: chunks } = useDocumentChunks(docId);
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Document Chunks</h2>
          <button onClick={onClose}><X className="w-6 h-6" /></button>
        </div>
        
        <div className="space-y-4">
          {chunks?.map((chunk, idx) => (
            <div key={idx} className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-gray-700">{chunk.type} - {chunk.section}</span>
                {chunk.score && <span className="text-xs text-gray-500">Score: {chunk.score.toFixed(4)}</span>}
              </div>
              <p className="text-sm text-gray-600">{chunk.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, className = '' }: any) {
  return (
    <div>
      <span className="text-sm font-semibold text-gray-700">{label}: </span>
      <span className={`text-sm text-gray-600 ${className}`}>{value}</span>
    </div>
  );
}
