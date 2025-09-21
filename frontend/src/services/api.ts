import { Client } from '@langchain/langgraph-sdk'
import {
  User,
  StartupSubmission,
  AnalysisResult,
  LoginForm,
  RegisterForm,
  StartupSubmissionForm,
  DashboardStats,
  PaginatedResponse,
  ChatMessage,
  Comment,
  AnalysisProgress,
} from '@/types'

// Base API configuration - Updated to use integrated server on port 8001
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8001'
const LANGGRAPH_URL = (import.meta as any).env?.VITE_LANGGRAPH_URL || 'http://localhost:8001'

// LangGraph client for agent communication
export const langGraphClient = new Client({ apiUrl: LANGGRAPH_URL })

// HTTP client with auth headers
class ApiClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  private getAuthHeaders(): Record<string, string> {
    const token = localStorage.getItem('minerva_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    }

    const response = await fetch(url, config)

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: 'An error occurred',
      }))
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  async upload<T>(endpoint: string, formData: FormData): Promise<T> {
    const token = localStorage.getItem('minerva_token')
    const headers: Record<string, string> = token
      ? { Authorization: `Bearer ${token}` }
      : {}

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: 'Upload failed',
      }))
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return response.json()
  }
}

const apiClient = new ApiClient(API_BASE_URL)

// Authentication API
export const authApi = {
  login: (data: LoginForm) =>
    apiClient.post<{ access_token: string; token_type: string; user_id: string }>(
      '/api/auth/login',
      data
    ),

  register: (data: RegisterForm) =>
    apiClient.post<{ access_token: string; token_type: string; user_id: string }>(
      '/api/auth/register',
      data
    ),

  logout: () => apiClient.post('/api/auth/logout'),

  getCurrentUser: () => apiClient.get<User>('/api/auth/me'),

  updateProfile: (data: Partial<User>) =>
    apiClient.put<User>('/api/auth/profile', data),

  changePassword: (data: { current_password: string; new_password: string }) =>
    apiClient.post('/api/auth/change-password', data),
}

// Startups API
export const startupsApi = {
  list: (params?: {
    page?: number
    per_page?: number
    industry?: string[]
    funding_stage?: string[]
    status?: string[]
    search?: string
  }) => {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v))
        } else if (value !== undefined) {
          searchParams.append(key, String(value))
        }
      })
    }
    return apiClient.get<PaginatedResponse<StartupSubmission>>(
      `/api/startups?${searchParams}`
    )
  },

  get: (id: string) =>
    apiClient.get<StartupSubmission>(`/api/startups/${id}`),

  create: (data: StartupSubmissionForm) =>
    apiClient.post<StartupSubmission>('/api/startups', data),

  update: (id: string, data: Partial<StartupSubmissionForm>) =>
    apiClient.put<StartupSubmission>(`/api/startups/${id}`, data),

  delete: (id: string) => apiClient.delete(`/api/startups/${id}`),

  updateStatus: (id: string, status: string) =>
    apiClient.put(`/api/startups/${id}/status`, { status }),

  uploadDocuments: (id: string, files: FileList) => {
    const formData = new FormData()
    Array.from(files).forEach(file => {
      formData.append('files', file)
    })
    return apiClient.upload<{ documents: any[] }>(
      `/api/startups/${id}/documents`,
      formData
    )
  },

  downloadDocument: (startupId: string, documentId: string) =>
    `${API_BASE_URL}/api/startups/${startupId}/documents/${documentId}/download`,
}

// Analysis API
export const analysisApi = {
  list: (params?: {
    page?: number
    per_page?: number
    startup_id?: string
    status?: string[]
  }) => {
    const searchParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach(v => searchParams.append(key, v))
        } else if (value !== undefined) {
          searchParams.append(key, String(value))
        }
      })
    }
    return apiClient.get<PaginatedResponse<AnalysisResult>>(
      `/api/analysis?${searchParams}`
    )
  },

  get: (id: string) =>
    apiClient.get<AnalysisResult>(`/api/analysis/${id}`),

  create: (startupId: string, options?: { priority?: string }) =>
    apiClient.post<{ analysis_id: string; message: string }>(
      '/api/analysis',
      { startup_id: startupId, ...options }
    ),

  getProgress: (analysisId: string) =>
    apiClient.get<AnalysisProgress>(`/api/analysis/${analysisId}/progress`),

  cancel: (id: string) =>
    apiClient.post(`/api/analysis/${id}/cancel`),

  export: (id: string, format: 'pdf' | 'docx' | 'json' = 'pdf') =>
    `${API_BASE_URL}/api/analysis/${id}/export?format=${format}`,

  // Agent communication via LangGraph
  startAnalysis: async (startupId: string, config?: any) => {
    try {
      const thread = await langGraphClient.threads.create()
      const run = await langGraphClient.runs.create(
        thread.thread_id,
        'minerva_analysis_agent',
        {
          input: {
            startup_id: startupId,
            config: config || {},
          }
        }
      )
      return { thread_id: thread.thread_id, run_id: run.run_id }
    } catch (error: any) {
      console.error('Failed to start analysis:', error)
      throw error
    }
  },

  getAnalysisStream: async (threadId: string, runId: string) => {
    try {
      return langGraphClient.runs.stream(threadId, runId)
    } catch (error) {
      console.error('Failed to get analysis stream:', error)
      throw error
    }
  },
}

// Comments API
export const commentsApi = {
  list: (startupId: string) =>
    apiClient.get<Comment[]>(`/api/startups/${startupId}/comments`),

  create: (startupId: string, data: {
    content: string
    comment_type?: string
    section?: string
    agent_type?: string
    parent_id?: string
  }) =>
    apiClient.post<Comment>(`/api/startups/${startupId}/comments`, data),

  update: (startupId: string, commentId: string, data: { content: string }) =>
    apiClient.put<Comment>(`/api/startups/${startupId}/comments/${commentId}`, data),

  delete: (startupId: string, commentId: string) =>
    apiClient.delete(`/api/startups/${startupId}/comments/${commentId}`),

  resolve: (startupId: string, commentId: string) =>
    apiClient.post(`/api/startups/${startupId}/comments/${commentId}/resolve`),

  like: (startupId: string, commentId: string) =>
    apiClient.post(`/api/startups/${startupId}/comments/${commentId}/like`),
}

// Chat API (Conversational Co-pilot)
export const chatApi = {
  getMessages: (startupId: string) =>
    apiClient.get<ChatMessage[]>(`/api/startups/${startupId}/chat`),

  sendMessage: (startupId: string, content: string, context?: any) =>
    apiClient.post<ChatMessage>(`/api/startups/${startupId}/chat`, {
      content,
      context,
    }),

  clearHistory: (startupId: string) =>
    apiClient.delete(`/api/startups/${startupId}/chat`),

  // Real-time chat via LangGraph
  createChatThread: async (startupId: string) => {
    try {
      const thread = await langGraphClient.threads.create({
        metadata: { startup_id: startupId, type: 'chat' },
      })
      return thread.thread_id
    } catch (error) {
      console.error('Failed to create chat thread:', error)
      throw error
    }
  },

  sendChatMessage: async (threadId: string, message: string) => {
    try {
      const run = await langGraphClient.runs.create(
        threadId,
        'minerva_chat_agent',
        {
          input: { message }
        }
      )
      return langGraphClient.runs.stream(threadId, run.run_id)
    } catch (error: any) {
      console.error('Failed to send chat message:', error)
      throw error
    }
  },
}

// Dashboard API
export const dashboardApi = {
  getStats: () => apiClient.get<DashboardStats>('/api/dashboard/stats'),

  getRecentActivity: () =>
    apiClient.get<any[]>('/api/dashboard/activity'),

  getInsights: () =>
    apiClient.get<any[]>('/api/dashboard/insights'),
}

// Utility functions
export const downloadFile = (url: string, filename: string) => {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export const getScoreColor = (score: number): string => {
  if (score >= 8) return 'text-success-600'
  if (score >= 6) return 'text-warning-600'
  if (score >= 4) return 'text-yellow-600'
  return 'text-danger-600'
}

export const getScoreLabel = (score: number): string => {
  if (score >= 8) return 'Excellent'
  if (score >= 6) return 'Good'
  if (score >= 4) return 'Fair'
  return 'Poor'
}
