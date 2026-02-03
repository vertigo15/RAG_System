import axios from 'axios';
import type { Document, DocumentChunk, Query, Settings, HealthStatus } from '../types';

export const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthApi = {
  getStatus: () => api.get<HealthStatus>('/health'),
};

export const documentsApi = {
  getAll: (options?: { status?: string; limit?: number; offset?: number }) =>
    api.get('/documents', { params: options }),
  getById: (id: string) => api.get<Document>(`/documents/${id}`),
  getChunks: (id: string) => api.get<DocumentChunk[]>(`/documents/${id}/chunks`),
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  delete: (id: string) => api.delete(`/documents/${id}`),
};

export const queriesApi = {
  submit: (query_text: string, document_ids?: string[]) =>
    api.post<Query>('/queries', { query_text, document_ids }),
  getById: (id: string) => api.get<Query>(`/queries/${id}`),
};

export const settingsApi = {
  get: () => api.get<Settings>('/settings'),
  update: (settings: Partial<Settings>) => api.put<Settings>('/settings', settings),
};
