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
import { auth } from '@/config/firebase'

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

  private async getAuthHeaders(): Promise<Record<string, string>> {
    // Get Firebase ID token if user is authenticated
    const user = auth.currentUser
    if (user) {
      try {
        const token = await user.getIdToken()
        return { Authorization: `Bearer ${token}` }
      } catch (error) {
        console.error('Failed to get Firebase ID token:', error)
        return {}
      }
    }
    return {}
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const authHeaders = await this.getAuthHeaders()
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
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
    const authHeaders = await this.getAuthHeaders()

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: authHeaders,
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
    apiClient.post<{ token: string; user: User }>(
      '/api/auth/login',
      data
    ),

  register: (data: RegisterForm) =>
    apiClient.post<{ token: string; user: User }>(
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

  // Re-analysis with investor notes
  triggerReanalysis: (startupId: string, investorNotes: string) =>
    apiClient.post<{ analysis_id: string; message: string; status: string }>(
      `/api/startups/${startupId}/reanalyze`,
      { investor_notes: investorNotes }
    ),

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
  // Legacy endpoint (keep for backward compatibility)
  getStats: () => apiClient.get<DashboardStats>('/api/dashboard/stats'),

  // New optimized endpoints
  getCoreStats: () => apiClient.get<{
    total_startups: number
    completed_analysis: number
    pending_analysis: number
  }>('/api/dashboard/core-stats'),

  getRecentStartups: (limit: number = 5) =>
    apiClient.get<any[]>(`/api/dashboard/recent-startups?limit=${limit}`),

  getBreakdowns: () => apiClient.get<{
    industry_breakdown: Array<{ name: string; value: number }>
    funding_stage_breakdown: Array<{ name: string; value: number }>
    product_stage_breakdown: Array<{ name: string; value: number }>
    company_structure_breakdown: Array<{ name: string; value: number }>
  }>('/api/dashboard/breakdowns'),

  getRecentActivity: (limit: number = 8) =>
    apiClient.get<any[]>(`/api/dashboard/activity?limit=${limit}`),
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

// Startup Status API
export const startupStatusApi = {
  getStatus: (startupId: string) =>
    apiClient.get<{
      startup_id: string
      investor_email: string
      status: string
      investor_note: string | null
      status_updated_at: string | null
      note_updated_at: string | null
    }>(`/api/startups/${startupId}/status`),

  updateStatus: (startupId: string, status: string) =>
    apiClient.put<{ success: boolean; startup_id: string; status: string; updated_at: string }>(
      `/api/startups/${startupId}/status`,
      { status }
    ),

  updateNote: (startupId: string, note: string) =>
    apiClient.put<{ success: boolean; startup_id: string; note: string; updated_at: string }>(
      `/api/startups/${startupId}/note`,
      { note }
    ),
}

// Beacon AI Agent API
export interface BeaconContextItem {
  section_id: string
  section_title: string
  section_type: string
  subsection?: string
}

export interface BeaconMessage {
  role: 'user' | 'agent' | 'system'
  content: string
  timestamp?: string
}

export interface BeaconToolCall {
  tool: string
  args: Record<string, any>
  result: {
    success: boolean
    message?: string
    error?: string
    [key: string]: any
  }
}

export interface BeaconChatRequest {
  startup_id: string
  message: string
  session_id: string  // Unique session ID for persistent conversations
  selected_section: string  // Section context from analysis page (empty string if none)
}

export interface BeaconChatResponse {
  success: boolean
  message: string
  tool_calls: BeaconToolCall[]
  finish_reason?: string
  error?: string
}

export const beaconApi = {
  /**
   * Chat with Beacon (non-streaming mode)
   * Uses Firestore-backed persistent sessions for automatic conversation history.
   * 
   * @param data - Chat request with startup_id, message, and session_id
   * @returns Complete response after agent finishes
   * 
   * @example
   * ```typescript
   * const sessionId = `${userId}_${startupId}`;
   * const response = await beaconApi.chat({
   *   startup_id: startupId,
   *   message: "What is the market size?",
   *   session_id: sessionId
   * });
   * ```
   */
  chat: (data: BeaconChatRequest) =>
    apiClient.post<BeaconChatResponse>('/api/beacon/chat', data),

  /**
   * Chat with Beacon (streaming mode)
   * Streams response in real-time using text/plain streaming.
   * Uses Firestore-backed persistent sessions for automatic conversation history.
   * 
   * @param data - Chat request with startup_id, message, and session_id
   * @returns Async generator yielding text chunks
   * 
   * @example
   * ```typescript
   * const sessionId = `${userId}_${startupId}`;
   * for await (const chunk of beaconApi.chatStream({
   *   startup_id: startupId,
   *   message: "What is the market size?",
   *   session_id: sessionId
   * })) {
   *   appendText(chunk);
   * }
   * ```
   */
  chatStream: async function* (data: BeaconChatRequest) {
    const token = await auth.currentUser?.getIdToken();
    const response = await fetch(`${API_BASE_URL}/api/beacon/chat-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Response body is not readable');
    }

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: false });
      yield text;
    }
  },

  health: () =>
    apiClient.get<{
      status: string
      service: string
      model: string
      features: string[]
    }>('/api/beacon/health'),
}
