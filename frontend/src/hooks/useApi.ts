import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsApi, queriesApi, settingsApi, healthApi } from '../services/api';

// Health
export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => healthApi.getStatus().then(res => res.data),
    refetchInterval: 10000,
  });
};

// Documents
export const useDocuments = () => {
  return useQuery({
    queryKey: ['documents'],
    queryFn: () => documentsApi.getAll().then(res => res.data),
    refetchInterval: 5000,
  });
};

export const useDocument = (id: string) => {
  return useQuery({
    queryKey: ['documents', id],
    queryFn: () => documentsApi.getById(id).then(res => res.data),
    enabled: !!id,
  });
};

export const useDocumentChunks = (id: string) => {
  return useQuery({
    queryKey: ['documents', id, 'chunks'],
    queryFn: () => documentsApi.getChunks(id).then(res => res.data),
    enabled: !!id,
  });
};

export const useUploadDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => documentsApi.upload(file).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });
};

// Queries
export const useQueryById = (id: string) => {
  return useQuery({
    queryKey: ['queries', id],
    queryFn: () => queriesApi.getById(id).then(res => res.data),
    enabled: !!id,
    refetchInterval: (query: any) => {
      if (query?.status === 'pending' || query?.status === 'processing') {
        return 2000; // Poll every 2s while processing
      }
      return false;
    },
  });
};

export const useSubmitQuery = () => {
  return useMutation({
    mutationFn: ({ query_text, document_ids }: { query_text: string; document_ids?: string[] }) =>
      queriesApi.submit(query_text, document_ids).then(res => res.data),
  });
};

// Settings
export const useSettings = () => {
  return useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsApi.get().then(res => res.data),
  });
};

export const useUpdateSettings = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (settings: any) => settingsApi.update(settings).then(res => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });
};
