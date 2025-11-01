/**
 * React hooks for Questions API
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { questionsApi } from '@/services/questions';
import type { QuestionRequest, AnswerRequest } from '@/types/questions';
import { useToast } from '@/hooks/use-toast';

// Query keys
export const questionKeys = {
  all: ['questions'] as const,
  startup: (startupId: string) => ['questions', 'startup', startupId] as const,
  startupByStatus: (startupId: string, status?: string) => 
    ['questions', 'startup', startupId, status] as const,
  myQuestions: () => ['questions', 'my'] as const,
  detail: (id: string) => ['questions', id] as const,
};

/**
 * Hook to get questions for a startup
 */
export function useStartupQuestions(startupId: string, status?: string) {
  return useQuery({
    queryKey: questionKeys.startupByStatus(startupId, status),
    queryFn: () => questionsApi.getStartupQuestions(startupId, status),
    enabled: !!startupId,
  });
}

/**
 * Hook to get questions asked by current user
 */
export function useMyQuestions() {
  return useQuery({
    queryKey: questionKeys.myQuestions(),
    queryFn: () => questionsApi.getMyQuestions(),
  });
}

/**
 * Hook to get a single question
 */
export function useQuestion(questionId: string) {
  return useQuery({
    queryKey: questionKeys.detail(questionId),
    queryFn: () => questionsApi.getQuestion(questionId),
    enabled: !!questionId,
  });
}

/**
 * Hook to create a question
 */
export function useCreateQuestion() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: QuestionRequest) => questionsApi.createQuestion(data),
    onSuccess: (newQuestion) => {
      // Invalidate startup questions
      queryClient.invalidateQueries({ 
        queryKey: questionKeys.startup(newQuestion.startup_id) 
      });
      
      toast({
        title: 'Question sent!',
        description: 'The founder will be notified of your question.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to send question',
        description: error.response?.data?.detail || 'Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook to answer a question
 */
export function useAnswerQuestion() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ questionId, data }: { questionId: string; data: AnswerRequest }) =>
      questionsApi.answerQuestion(questionId, data),
    onSuccess: (updatedQuestion) => {
      // Invalidate queries
      queryClient.invalidateQueries({ 
        queryKey: questionKeys.startup(updatedQuestion.startup_id) 
      });
      queryClient.invalidateQueries({ 
        queryKey: questionKeys.detail(updatedQuestion.id) 
      });
      
      toast({
        title: 'Answer submitted!',
        description: 'The investor will be notified of your response.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to submit answer',
        description: error.response?.data?.detail || 'Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook to update a question
 */
export function useUpdateQuestion() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ questionId, data }: { questionId: string; data: Partial<QuestionRequest> }) =>
      questionsApi.updateQuestion(questionId, data),
    onSuccess: (updatedQuestion) => {
      queryClient.invalidateQueries({ 
        queryKey: questionKeys.startup(updatedQuestion.startup_id) 
      });
      queryClient.invalidateQueries({ 
        queryKey: questionKeys.detail(updatedQuestion.id) 
      });
      
      toast({
        title: 'Question updated',
        description: 'Your question has been updated successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to update question',
        description: error.response?.data?.detail || 'Please try again.',
        variant: 'destructive',
      });
    },
  });
}

/**
 * Hook to delete a question
 */
export function useDeleteQuestion() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (questionId: string) => questionsApi.deleteQuestion(questionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: questionKeys.all });
      
      toast({
        title: 'Question deleted',
        description: 'The question has been removed.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete question',
        description: error.response?.data?.detail || 'Please try again.',
        variant: 'destructive',
      });
    },
  });
}
