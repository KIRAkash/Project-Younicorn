/**
 * API service for Questions, Notifications, and Activity
 */
import { auth } from '@/config/firebase';
import type { Question, QuestionRequest, AnswerRequest, Notification, Activity } from '@/types/questions';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

// Helper to get auth headers
async function getAuthHeaders(): Promise<Record<string, string>> {
  const user = auth.currentUser;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  if (user) {
    const token = await user.getIdToken();
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

// Helper for API requests
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const authHeaders = await getAuthHeaders();
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      ...authHeaders,
      ...(options.headers as Record<string, string> || {}),
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// ==================== Questions API ====================

export const questionsApi = {
  /**
   * Create a new question (Investor only)
   */
  createQuestion: async (data: QuestionRequest): Promise<Question> => {
    return apiRequest<Question>('/api/questions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get a single question by ID
   */
  getQuestion: async (questionId: string): Promise<Question> => {
    return apiRequest<Question>(`/api/questions/${questionId}`);
  },

  /**
   * Answer a question (Founder only)
   */
  answerQuestion: async (questionId: string, data: AnswerRequest): Promise<Question> => {
    return apiRequest<Question>(`/api/questions/${questionId}/answer`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get all questions for a startup
   */
  getStartupQuestions: async (startupId: string, status?: string): Promise<Question[]> => {
    return apiRequest<Question[]>(`/api/questions/startup/${startupId}${status ? `?status=${status}` : ''}`);
  },

  /**
   * Get questions asked by current user (Investor only)
   */
  getMyQuestions: async (): Promise<Question[]> => {
    return apiRequest<Question[]>('/api/questions/my-questions');
  },

  /**
   * Update a question
   */
  updateQuestion: async (questionId: string, data: Partial<QuestionRequest>): Promise<Question> => {
    return apiRequest<Question>(`/api/questions/${questionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a question
   */
  deleteQuestion: async (questionId: string): Promise<void> => {
    await apiRequest<void>(`/api/questions/${questionId}`, {
      method: 'DELETE',
    });
  },
};

// ==================== Notifications API ====================

export const notificationsApi = {
  /**
   * Get notifications for current user
   */
  getNotifications: async (unreadOnly = false, limit = 50): Promise<Notification[]> => {
    return apiRequest<Notification[]>(`/api/notifications?unread_only=${unreadOnly}&limit=${limit}`);
  },

  /**
   * Get unread notification count
   */
  getUnreadCount: async (): Promise<number> => {
    const response = await apiRequest<{ count: number }>('/api/notifications/unread/count');
    return response.count;
  },

  /**
   * Mark notification as read
   */
  markAsRead: async (notificationId: string): Promise<void> => {
    await apiRequest<void>(`/api/notifications/${notificationId}/read`, {
      method: 'PUT',
    });
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async (): Promise<void> => {
    await apiRequest<void>('/api/notifications/read-all', {
      method: 'PUT',
    });
  },

  /**
   * Delete a notification
   */
  deleteNotification: async (notificationId: string): Promise<void> => {
    await apiRequest<void>(`/api/notifications/${notificationId}`, {
      method: 'DELETE',
    });
  },
};

// ==================== Activity API ====================

export const activityApi = {
  /**
   * Get activity feed for a startup
   */
  getStartupActivity: async (startupId: string, limit = 50): Promise<Activity[]> => {
    return apiRequest<Activity[]>(`/api/activity/startup/${startupId}?limit=${limit}`);
  },

  /**
   * Get activity feed for current user
   */
  getMyActivity: async (limit = 50): Promise<Activity[]> => {
    return apiRequest<Activity[]>(`/api/activity/me?limit=${limit}`);
  },
};
