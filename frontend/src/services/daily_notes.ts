import api from './api'
import { Note } from './notes'

export interface DailyNote {
  id: string
  user_id: string
  note_date: string
  content: string | null
  created_at: string
  updated_at: string
  linked_note_ids?: string[]
}

export interface DailyNoteLink {
  id: string
  daily_note_id: string
  note_id: string
  created_at: string
}

export interface DailyNoteCreate {
  note_date: string
  content?: string
}

export interface DailyNoteUpdate {
  content?: string
}

class DailyNotesService {
  /**
   * Create or update a daily note for a specific date
   */
  async createOrUpdateDailyNote(data: DailyNoteCreate): Promise<DailyNote> {
    const response = await api.post<DailyNote>('/daily/', data)
    return response.data
  }

  /**
   * Get all daily notes with pagination
   */
  async getDailyNotes(skip: number = 0, limit: number = 100): Promise<DailyNote[]> {
    const response = await api.get<DailyNote[]>('/daily/', {
      params: { skip, limit }
    })
    return response.data
  }

  /**
   * Get a daily note for a specific date
   */
  async getDailyNoteByDate(date: string): Promise<DailyNote> {
    const response = await api.get<DailyNote>(`/daily/${date}`)
    return response.data
  }

  /**
   * Update a daily note by ID
   */
  async updateDailyNote(dailyNoteId: string, data: DailyNoteUpdate): Promise<DailyNote> {
    const response = await api.put<DailyNote>(`/daily/${dailyNoteId}`, data)
    return response.data
  }

  /**
   * Delete a daily note
   */
  async deleteDailyNote(dailyNoteId: string): Promise<void> {
    await api.delete(`/daily/${dailyNoteId}`)
  }

  /**
   * Get today's date in YYYY-MM-DD format
   */
  getTodayDate(): string {
    const today = new Date()
    return today.toISOString().split('T')[0]
  }

  /**
   * Link a note to a daily note
   */
  async linkNoteToDailyNote(dailyNoteId: string, noteId: string): Promise<DailyNoteLink> {
    const response = await api.post<DailyNoteLink>(`/daily/${dailyNoteId}/links/${noteId}`)
    return response.data
  }

  /**
   * Get all notes linked to a daily note
   */
  async getLinkedNotes(dailyNoteId: string): Promise<Note[]> {
    const response = await api.get<Note[]>(`/daily/${dailyNoteId}/linked-notes`)
    return response.data
  }

  /**
   * Unlink a note from a daily note
   */
  async unlinkNoteFromDailyNote(dailyNoteId: string, noteId: string): Promise<void> {
    await api.delete(`/daily/${dailyNoteId}/links/${noteId}`)
  }

  /**
   * Link a note to today's daily note (auto-creates today's note if needed)
   */
  async linkNoteToToday(noteId: string): Promise<DailyNoteLink> {
    const response = await api.post<DailyNoteLink>(`/daily/link-to-today/${noteId}`)
    return response.data
  }
}

export const dailyNotesService = new DailyNotesService()
export default dailyNotesService
