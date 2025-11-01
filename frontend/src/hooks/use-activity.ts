/**
 * React hooks for Activity Feed API
 */
import { useQuery } from '@tanstack/react-query';
import { activityApi } from '@/services/questions';

// Query keys
export const activityKeys = {
  all: ['activity'] as const,
  startup: (startupId: string) => ['activity', 'startup', startupId] as const,
  my: () => ['activity', 'my'] as const,
};

/**
 * Hook to get activity feed for a startup
 */
export function useStartupActivity(startupId: string, limit = 50) {
  return useQuery({
    queryKey: activityKeys.startup(startupId),
    queryFn: () => activityApi.getStartupActivity(startupId, limit),
    enabled: !!startupId,
    refetchInterval: 60000, // Refetch every minute
  });
}

/**
 * Hook to get activity feed for current user
 */
export function useMyActivity(limit = 50) {
  return useQuery({
    queryKey: activityKeys.my(),
    queryFn: () => activityApi.getMyActivity(limit),
    refetchInterval: 60000, // Refetch every minute
  });
}
