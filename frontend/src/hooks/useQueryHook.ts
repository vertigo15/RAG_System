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
