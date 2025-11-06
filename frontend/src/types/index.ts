// Type definitions for Aura frontend

export interface User {
  id: string
  email: string
  createdAt: string
}

export interface Note {
  id: string
  userId: string
  title: string
  content: string
  type: 'text' | 'audio' | 'image' | 'pdf' | 'link'
  createdAt: string
  updatedAt: string
}

export interface DailyNote {
  id: string
  userId: string
  date: string
  content: string
  linkedNoteIds?: string[]
}

export interface DailyNoteLink {
  id: string
  dailyNoteId: string
  noteId: string
  createdAt: string
}

export interface Area {
  id: string
  userId: string
  name: string
  description: string
  icon?: string
  order: number
}

export interface Project {
  id: string
  userId: string
  areaId?: string
  name: string
  status: 'active' | 'completed' | 'archived'
  dueDate?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
}

export interface ProcessingJob {
  id: string
  note_id: string
  media_id?: string
  job_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface ProcessedContent {
  id: string
  note_id: string
  content_type: string
  raw_text?: string
  summary?: string
  key_points: string[]
  extracted_tasks: string[]
  metadata: Record<string, any>
  confidence_score?: number
  created_at: string
}

export type ClassificationType =
  | 'task'
  | 'log_entry'
  | 'thought'
  | 'meeting_note'
  | 'invoice'
  | 'email'
  | 'reference'
  | 'other'

export type Priority = 'low' | 'medium' | 'high' | 'urgent'

export interface TextClassification {
  id: string
  note_id: string
  classification_type: ClassificationType
  confidence: number
  suggested_area?: string
  suggested_project?: string
  is_actionable: boolean
  priority?: Priority
  created_at: string
}
