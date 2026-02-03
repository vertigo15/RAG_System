import { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from './useToast';
import { documentsApi } from '../services/api';
import { Document } from '../types';

export interface UseDocumentsOptions {
  searchQuery?: string;
  statusFilter?: string | null;
  page?: number;
  pageSize?: number;
}

export function useDocuments(options?: UseDocumentsOptions) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [page, setPage] = useState(options?.page || 1);
  const [pageSize] = useState(options?.pageSize || 10);
  const [searchQuery, setSearchQuery] = useState(options?.searchQuery || '');
  const [statusFilter, setStatusFilter] = useState(options?.statusFilter || null);

  const { data: response, isLoading, refetch } = useQuery({
    queryKey: ['documents', statusFilter, page, pageSize],
    queryFn: async () => {
      const offset = (page - 1) * pageSize;
      const params: any = { limit: pageSize, offset };
      if (statusFilter) {
        params.status = statusFilter;
      }
      try {
        const result = await documentsApi.getAll(params);
        return result?.data || { documents: [], total: 0 };
      } catch (err) {
        console.error('Failed to fetch documents:', err);
        return { documents: [], total: 0 };
      }
    },
    refetchInterval: 10000,
  });

  // Handle both response formats: {data, total} and {documents, total}
  const documents = (response?.data || response?.documents || []) as Document[];
  const total = response?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  // Client-side search filtering
  const filteredDocuments = useMemo(() => {
    if (!searchQuery) return documents;
    const query = searchQuery.toLowerCase();
    return documents.filter((doc: Document) =>
      doc.filename.toLowerCase().includes(query) ||
      (doc.tags?.some(tag => tag.toLowerCase().includes(query)) || false) ||
      (doc.summary?.toLowerCase().includes(query) || false)
    );
  }, [documents, searchQuery]);

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const file = files[0];
      return documentsApi.upload(file);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document uploaded successfully');
      setPage(1);
    },
    onError: (error: any) => {
      toast.error(error.message || 'Upload failed');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document deleted');
    },
  });

  return {
    documents: filteredDocuments,
    isLoading,
    uploadDocument: uploadMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    isUploading: uploadMutation.isPending,
    isDeleting: deleteMutation.isPending,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    page,
    setPage,
    pageSize,
    total,
    totalPages,
    refetch,
  };
}
