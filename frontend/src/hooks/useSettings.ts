import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings } from '../types';
import { useToast } from './useToast';
import { settingsApi, healthApi } from '../services/api';

export function useSettings() {
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await settingsApi.get();
      return response.data;
    },
  });

  const updateMutation = useMutation({
    mutationFn: (newSettings: Partial<Settings>) => 
      settingsApi.update(newSettings),
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
      const response = await healthApi.getStatus();
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
