// Core types for Project Minerva

export interface User {
  id: string
  email: string
  full_name: string
  role: 'founder' | 'investor' | 'analyst' | 'admin'
  status: 'active' | 'inactive' | 'pending' | 'suspended'
  company?: string
  title?: string
  bio?: string
  avatar_url?: string
  created_at: string
  last_login?: string
  email_notifications: boolean
  timezone: string
}

export interface StartupSubmission {
  id: string
  company_info: CompanyInfo
  founders: FounderInfo[]
  documents: StartupDocument[]
  metadata: StartupMetadata
  submitted_by: string
  submission_timestamp: string
  last_updated: string
  analysis_requested: boolean
  analysis_started?: string
  analysis_completed?: string
  status: string
}

export interface CompanyInfo {
  name: string
  description: string
  website_url?: string
  industry: Industry
  funding_stage: FundingStage
  location: string
  founded_date?: string
  employee_count?: number
  revenue_run_rate?: number
  funding_raised?: number
  funding_seeking?: number
}

export interface FounderInfo {
  name: string
  email: string
  linkedin_url?: string
  role: string
  bio?: string
  previous_experience: string[]
  education: string[]
}

export interface StartupDocument {
  id: string
  filename: string
  document_type: DocumentType
  file_size: number
  mime_type: string
  storage_path: string
  upload_timestamp: string
  processed: boolean
  extracted_text?: string
  metadata: Record<string, any>
}

export interface StartupMetadata {
  key_metrics: Record<string, any>
  competitive_advantages: string[]
  target_market?: string
  business_model?: string
  traction_highlights: string[]
  use_of_funds?: string
  exit_strategy?: string
}

export interface AnalysisResult {
  id: string
  startup_id: string
  request_id: string
  agent_analyses: Record<AgentType, AgentAnalysis>
  investability_score?: InvestabilityScore
  risks_opportunities: RiskOpportunity[]
  executive_summary?: string
  investment_memo?: string
  key_insights: string[]
  status: AnalysisStatus
  started_at?: string
  completed_at?: string
  total_duration_seconds?: number
  overall_confidence?: number
  data_completeness?: number
  version: number
  last_updated: string
}

export interface AgentAnalysis {
  agent_type: AgentType
  score: number
  summary: string
  detailed_analysis: string
  key_findings: string[]
  supporting_evidence: string[]
  sources: SourceCitation[]
  confidence_level: number
  execution_trace: AgentTrace[]
  started_at: string
  completed_at?: string
  duration_seconds?: number
}

export interface InvestabilityScore {
  overall_score: number
  team_score: number
  market_score: number
  product_score: number
  competition_score: number
  score_weights: Record<string, number>
  investment_recommendation: string
  confidence_level: number
}

export interface RiskOpportunity {
  type: 'risk' | 'opportunity'
  level: string
  title: string
  description: string
  impact: string
  mitigation?: string
  sources: SourceCitation[]
}

export interface SourceCitation {
  id: string
  title: string
  url?: string
  domain?: string
  document_name?: string
  page_number?: number
  excerpt?: string
  confidence_score?: number
}

export interface AgentTrace {
  step_number: number
  action: string
  reasoning?: string
  tool_used?: string
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  timestamp: string
  duration_seconds?: number
}

export interface Comment {
  id: string
  startup_id: string
  user_id: string
  parent_id?: string
  content: string
  comment_type: CommentType
  section?: string
  agent_type?: string
  is_resolved: boolean
  resolved_by?: string
  resolved_at?: string
  created_at: string
  updated_at: string
  likes: number
}

export interface ChatMessage {
  id: string
  startup_id: string
  user_id: string
  content: string
  message_type: 'user' | 'assistant'
  context: Record<string, any>
  agent_used?: string
  confidence_score?: number
  sources_cited: string[]
  created_at: string
}

export interface AnalysisProgress {
  total_steps: number
  completed_steps: number
  current_agent: string
  status: 'starting' | 'in_progress' | 'completed' | 'failed'
  progress_percentage: number
  started_at?: string
  completed_at?: string
  last_updated: string
}

// Enums
export type Industry = 
  | 'fintech'
  | 'healthtech'
  | 'edtech'
  | 'enterprise_software'
  | 'consumer_apps'
  | 'ecommerce'
  | 'ai_ml'
  | 'blockchain'
  | 'cybersecurity'
  | 'climate_tech'
  | 'biotech'
  | 'hardware'
  | 'other'

export type FundingStage = 
  | 'pre_seed'
  | 'seed'
  | 'series_a'
  | 'series_b'
  | 'series_c'
  | 'later_stage'

export type DocumentType = 
  | 'pitch_deck'
  | 'business_plan'
  | 'financial_model'
  | 'product_demo'
  | 'market_research'
  | 'team_bios'
  | 'legal_docs'
  | 'other'

export type AnalysisStatus = 
  | 'pending'
  | 'in_progress'
  | 'completed'
  | 'failed'
  | 'cancelled'

export type AgentType = 
  | 'orchestrator'
  | 'team'
  | 'market'
  | 'product'
  | 'competition'
  | 'synthesis'

export type CommentType = 
  | 'general'
  | 'question'
  | 'concern'
  | 'positive'
  | 'action_item'

export type StartupStatus = 
  | 'new'
  | 'reviewing'
  | 'shortlisted'
  | 'due_diligence'
  | 'term_sheet'
  | 'rejected'
  | 'watching'
  | 'invested'

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface ErrorResponse {
  error: string
  message: string
  details?: Record<string, any>
}

// Form types
export interface LoginForm {
  email: string
  password: string
}

export interface RegisterForm {
  email: string
  full_name: string
  password: string
  confirm_password: string
  role: 'founder' | 'investor'
  company?: string
  title?: string
  terms: boolean
}

export interface StartupSubmissionForm {
  company_info: Omit<CompanyInfo, 'industry' | 'funding_stage'> & {
    industry: string
    funding_stage: string
  }
  founders: FounderInfo[]
  documents: File[]
  metadata: StartupMetadata
}

// Chart data types
export interface ChartData {
  name: string
  value: number
  color?: string
}

export interface TimeSeriesData {
  date: string
  value: number
  label?: string
}

// Dashboard types
export interface DashboardStats {
  total_startups: number
  pending_analysis: number
  completed_analysis: number
  avg_score: number
  recent_submissions: StartupSubmission[]
  industry_breakdown: ChartData[]
  funding_stage_breakdown: ChartData[]
  monthly_submissions: TimeSeriesData[]
}

// Filter types
export interface StartupFilters {
  industry?: Industry[]
  funding_stage?: FundingStage[]
  status?: StartupStatus[]
  score_range?: [number, number]
  date_range?: [string, string]
  search?: string
}

export interface AnalysisFilters {
  status?: AnalysisStatus[]
  score_range?: [number, number]
  confidence_range?: [number, number]
  date_range?: [string, string]
  agent_type?: AgentType[]
}
