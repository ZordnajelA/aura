import api from './api'

export interface MediaInfo {
  id: string
  file_path: string
  file_type: string
  file_size: number | null
  mime_type: string | null
  url: string
}

export interface Note {
  id: string
  user_id: string
  title: string | null
  content: string | null
  note_type: string
  created_at: string
  updated_at: string
  media_files?: MediaInfo[]
}

export interface NoteCreate {
  title?: string
  content?: string
  note_type?: string
}

export interface NoteUpdate {
  title?: string
  content?: string
  note_type?: string
}

class NotesService {
  /**
   * Create a new note
   */
  async createNote(data: NoteCreate): Promise<Note> {
    const response = await api.post<Note>('/notes/', data)
    return response.data
  }

  /**
   * Get all notes with pagination
   */
  async getNotes(skip: number = 0, limit: number = 100): Promise<Note[]> {
    const response = await api.get<Note[]>('/notes/', {
      params: { skip, limit }
    })
    return response.data
  }

  /**
   * Get a specific note by ID
   */
  async getNote(noteId: string): Promise<Note> {
    const response = await api.get<Note>(`/notes/${noteId}`)
    return response.data
  }

  /**
   * Update a note
   */
  async updateNote(noteId: string, data: NoteUpdate): Promise<Note> {
    const response = await api.put<Note>(`/notes/${noteId}`, data)
    return response.data
  }

  /**
   * Delete a note
   */
  async deleteNote(noteId: string): Promise<void> {
    await api.delete(`/notes/${noteId}`)
  }

  /**
   * Get all areas linked to a note
   */
  async getNoteAreas(noteId: string): Promise<any[]> {
    const response = await api.get(`/notes/${noteId}/areas`)
    return response.data
  }

  /**
   * Get all projects linked to a note
   */
  async getNoteProjects(noteId: string): Promise<any[]> {
    const response = await api.get(`/notes/${noteId}/projects`)
    return response.data
  }

  /**
   * Get all resources linked to a note
   */
  async getNoteResources(noteId: string): Promise<any[]> {
    const response = await api.get(`/notes/${noteId}/resources`)
    return response.data
  }
}

export const notesService = new NotesService()
export default notesService
