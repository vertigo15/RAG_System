# Script to create all remaining frontend components
# Run this to complete the frontend implementation

$baseDir = "C:\Users\user\OneDrive - JeenAI\Documents\code\RAG_System\frontend\src"

Write-Host "Creating all remaining components..." -ForegroundColor Green

# Component templates as a hash table
$components = @{
    "useDocuments.ts" = @"
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Document } from '../types';
import { useToast } from './useToast';
import api from '../services/api';

export function useDocuments() {
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await api.get('/documents');
      return response.data;
    },
    refetchInterval: 10000,
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const formData = new FormData();
      Array.from(files).forEach((file) => {
        formData.append('files', file);
      });
      return api.post('/documents/upload', formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document uploaded successfully');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Upload failed');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/documents/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document deleted');
    },
  });

  return {
    documents,
    isLoading,
    uploadDocument: uploadMutation.mutate,
    deleteDocument: deleteMutation.mutate,
    isUploading: uploadMutation.isPending,
  };
}
"@

    "useSettings.ts" = @"
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings } from '../types';
import { useToast } from './useToast';
import api from '../services/api';

export function useSettings() {
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await api.get('/settings');
      return response.data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: (newSettings: Partial<Settings>) => 
      api.put('/settings', newSettings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      toast.success('Settings updated');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Update failed');
    },
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get('/health');
      return response.data;
    },
    refetchInterval: 30000,
  });

  return {
    settings,
    health,
    isLoading,
    updateSettings: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}
"@

    "useQueryHook.ts" = @"
import { useMutation } from '@tanstack/react-query';
import { QueryRequest, QueryResponse } from '../types';
import { useToast } from './useToast';
import api from '../services/api';

export function useQuerySubmit() {
  const toast = useToast();

  const submitMutation = useMutation({
    mutationFn: async (request: QueryRequest) => {
      const response = await api.post('/queries', request);
      return response.data;
    },
    onError: (error: any) => {
      toast.error(error.message || 'Query failed');
    },
  });

  return {
    submitQuery: submitMutation.mutate,
    result: submitMutation.data as QueryResponse | undefined,
    isLoading: submitMutation.isPending,
    error: submitMutation.error,
  };
}
"@
}

# Create hooks
Write-Host "`nCreating hooks..." -ForegroundColor Yellow
foreach ($file in $components.Keys) {
    $filePath = Join-Path "$baseDir\hooks" $file
    $components[$file] | Out-File -FilePath $filePath -Encoding UTF8
    Write-Host "Created $file" -ForegroundColor Cyan
}

Write-Host "`n✓ All components created!" -ForegroundColor Green
Write-Host "`nNext: Run 'npm install' and 'npm run dev' in the frontend directory" -ForegroundColor Yellow
"@