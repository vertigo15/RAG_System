import { useMutation } from '@tanstack/react-query';
import { QueryRequest, QueryResponse } from '../types';
import { useToast } from './useToast';
import { queriesApi } from '../services/api';

export function useQuerySubmit() {
  const toast = useToast();

  const submitMutation = useMutation({
    mutationFn: async (request: QueryRequest) => {
      const response = await queriesApi.submit(request.query_text, request.document_filter);
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
