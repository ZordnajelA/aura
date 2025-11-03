import { useState, useEffect } from 'react'
import { Calendar, Plus, Loader2 } from 'lucide-react'
import Navigation from '@/components/Navigation'
import dailyNotesService, { DailyNote } from '@/services/daily_notes'

export default function DailyNotesPage() {
  const [dailyNotes, setDailyNotes] = useState<DailyNote[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDate] = useState<string>(dailyNotesService.getTodayDate())
  const [editingContent, setEditingContent] = useState<string>('')
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    loadDailyNotes()
  }, [])

  const loadDailyNotes = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const notes = await dailyNotesService.getDailyNotes(0, 30)
      setDailyNotes(notes)
    } catch (err) {
      console.error('Error loading daily notes:', err)
      setError('Failed to load daily notes')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveDailyNote = async () => {
    if (!editingContent.trim()) return

    try {
      setIsSaving(true)
      setError(null)
      await dailyNotesService.createOrUpdateDailyNote({
        note_date: selectedDate,
        content: editingContent
      })
      setEditingContent('')
      await loadDailyNotes()
    } catch (err) {
      console.error('Error saving daily note:', err)
      setError('Failed to save daily note')
    } finally {
      setIsSaving(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const isToday = (dateString: string) => {
    return dateString === dailyNotesService.getTodayDate()
  }

  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Calendar className="w-8 h-8" />
              Daily Notes
            </h1>
          </div>

          {/* Create/Edit Today's Note */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">
                {formatDate(selectedDate)}
                {isToday(selectedDate) && (
                  <span className="ml-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">Today</span>
                )}
              </h2>
            </div>
            <textarea
              value={editingContent}
              onChange={(e) => setEditingContent(e.target.value)}
              placeholder="What's on your mind today? Capture your thoughts, ideas, and reflections..."
              className="w-full border rounded-lg p-4 min-h-[150px] focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleSaveDailyNote}
                disabled={!editingContent.trim() || isSaving}
                className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Save Daily Note
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Timeline of Daily Notes */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>

            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
              </div>
            ) : dailyNotes.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <Calendar className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p className="text-gray-500">No daily notes yet. Start writing above!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {dailyNotes.map((note) => (
                  <div
                    key={note.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-800">
                        {formatDate(note.note_date)}
                      </h3>
                      {isToday(note.note_date) && (
                        <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">Today</span>
                      )}
                    </div>
                    <div className="text-gray-700 whitespace-pre-wrap">
                      {note.content || <span className="text-gray-400 italic">No content</span>}
                    </div>
                    <div className="mt-4 text-xs text-gray-500">
                      Last updated: {new Date(note.updated_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
