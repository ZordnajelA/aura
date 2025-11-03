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
  noteId: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  result?: any
}
