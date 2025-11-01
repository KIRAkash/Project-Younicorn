/**
 * TypeScript types for Q&A feature
 */

export type QuestionCategory = 'team' | 'market' | 'product' | 'financials' | 'business_model';
export type QuestionPriority = 'low' | 'medium' | 'high';
export type QuestionStatus = 'pending' | 'answered' | 'clarification_needed';

export interface AnswerAttachment {
  filename: string;
  gcs_path: string;
  size: number;
  uploaded_at?: string;
}

export interface Answer {
  answered_by: string;
  answered_by_name: string;
  answer_text: string;
  attachments: AnswerAttachment[];
  answered_at?: string;
  updated_at?: string;
}

export interface Question {
  id: string;
  startup_id: string;
  asked_by: string;
  asked_by_name: string;
  asked_by_role: string;
  question_text: string;
  category: QuestionCategory;
  priority: QuestionPriority;
  status: QuestionStatus;
  is_ai_generated: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
  answer?: Answer;
}

export interface QuestionRequest {
  startup_id: string;
  question_text: string;
  category: QuestionCategory;
  priority: QuestionPriority;
  tags?: string[];
}

export interface AnswerRequest {
  answer_text: string;
  attachments?: AnswerAttachment[];
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  related_id: string;
  related_type: string;
  read: boolean;
  created_at: string;
}

export interface Activity {
  id: string;
  startup_id: string;
  user_id: string;
  user_name: string;
  activity_type: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}
