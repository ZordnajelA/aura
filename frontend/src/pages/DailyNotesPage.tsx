import { useState, useEffect } from 'react'
import { Calendar, Plus, Loader2, ChevronLeft, ChevronRight, Link as LinkIcon, X } from 'lucide-react'
import Navigation from '@/components/Navigation'
import CalendarView from '@/components/CalendarView'
import dailyNotesService, { DailyNote } from '@/services/daily_notes'
import notesService, { Note } from '@/services/notes'

export default function DailyNotesPage() {
  const [, setDailyNotes] = useState<DailyNote[]>([])
  const [currentDailyNote, setCurrentDailyNote] = useState<DailyNote | null>(null)
  const [linkedNotes, setLinkedNotes] = useState<Note[]>([])
  const [allNotes, setAllNotes] = useState<Note[]>([])
  const [, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedDate, setSelectedDate] = useState<Date>(new Date())
  const [editingContent, setEditingContent] = useState<string>('')
  const [isSaving, setIsSaving] = useState(false)
  const [showCalendar, setShowCalendar] = useState(false)
  const [showLinkModal, setShowLinkModal] = useState(false)
  const [datesWithNotes, setDatesWithNotes] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadDailyNotes()
    loadAllNotes()
  }, [])

  useEffect(() => {
    loadDailyNoteForDate(selectedDate)
  }, [selectedDate])

  const formatDateKey = (date: Date): string => {
    return date.toISOString().split('T')[0]
  }

  const loadDailyNotes = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const notes = await dailyNotesService.getDailyNotes(0, 100)
      setDailyNotes(notes)

      // Build set of dates that have notes
      const dates = new Set(notes.map(n => n.note_date))
      setDatesWithNotes(dates)
    } catch (err) {
      console.error('Error loading daily notes:', err)
      setError('Failed to load daily notes')
    } finally {
      setIsLoading(false)
    }
  }

  const loadAllNotes = async () => {
    try {
      const notes = await notesService.getNotes(0, 100)
      setAllNotes(notes)
    } catch (err) {
      console.error('Error loading notes:', err)
    }
  }

  const loadDailyNoteForDate = async (date: Date) => {
    const dateKey = formatDateKey(date)
    try {
      const note = await dailyNotesService.getDailyNoteByDate(dateKey)
      setCurrentDailyNote(note)
      setEditingContent(note.content || '')

      // Load linked notes
      if (note.id) {
        const linked = await dailyNotesService.getLinkedNotes(note.id)
        setLinkedNotes(linked)
      }
    } catch (err: any) {
      // 404 means no note for this date yet
      if (err.response?.status === 404) {
        setCurrentDailyNote(null)
        setEditingContent('')
        setLinkedNotes([])
      } else {
        console.error('Error loading daily note:', err)
      }
    }
  }

  const handleSaveDailyNote = async () => {
    try {
      setIsSaving(true)
      setError(null)
      const dateKey = formatDateKey(selectedDate)
      const saved = await dailyNotesService.createOrUpdateDailyNote({
        note_date: dateKey,
        content: editingContent
      })
      setCurrentDailyNote(saved)
      await loadDailyNotes()
    } catch (err) {
      console.error('Error saving daily note:', err)
      setError('Failed to save daily note')
    } finally {
      setIsSaving(false)
    }
  }

  const handleLinkNote = async (noteId: string) => {
    if (!currentDailyNote) {
      // Create daily note first
      await handleSaveDailyNote()
      // Wait a bit for the note to be created
      await new Promise(resolve => setTimeout(resolve, 500))
      // Reload to get the ID
      await loadDailyNoteForDate(selectedDate)
    }

    try {
      if (currentDailyNote?.id) {
        await dailyNotesService.linkNoteToDailyNote(currentDailyNote.id, noteId)
        const linked = await dailyNotesService.getLinkedNotes(currentDailyNote.id)
        setLinkedNotes(linked)
      }
    } catch (err) {
      console.error('Error linking note:', err)
      setError('Failed to link note')
    }
  }

  const handleUnlinkNote = async (noteId: string) => {
    if (!currentDailyNote?.id) return

    try {
      await dailyNotesService.unlinkNoteFromDailyNote(currentDailyNote.id, noteId)
      const linked = await dailyNotesService.getLinkedNotes(currentDailyNote.id)
      setLinkedNotes(linked)
    } catch (err) {
      console.error('Error unlinking note:', err)
      setError('Failed to unlink note')
    }
  }

  const handlePreviousDay = () => {
    const newDate = new Date(selectedDate)
    newDate.setDate(newDate.getDate() - 1)
    setSelectedDate(newDate)
  }

  const handleNextDay = () => {
    const newDate = new Date(selectedDate)
    newDate.setDate(newDate.getDate() + 1)
    setSelectedDate(newDate)
  }

  const handleToday = () => {
    setSelectedDate(new Date())
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const isToday = (date: Date) => {
    const today = new Date()
    return formatDateKey(date) === formatDateKey(today)
  }

  const getAvailableNotesToLink = () => {
    const linkedNoteIds = new Set(linkedNotes.map(n => n.id))
    return allNotes.filter(n => !linkedNoteIds.has(n.id))
  }

  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Calendar className="w-8 h-8" />
              Daily Notes
            </h1>
            <button
              onClick={() => setShowCalendar(!showCalendar)}
              className="px-4 py-2 bg-white border rounded-lg hover:bg-gray-50 transition-colors"
            >
              {showCalendar ? 'Hide Calendar' : 'Show Calendar'}
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main content area */}
            <div className="lg:col-span-2 space-y-6">
              {/* Date Navigation */}
              <div className="bg-white rounded-lg shadow-md p-4">
                <div className="flex items-center justify-between">
                  <button
                    onClick={handlePreviousDay}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>

                  <div className="text-center">
                    <h2 className="text-xl font-semibold">
                      {formatDate(selectedDate)}
                    </h2>
                    {isToday(selectedDate) && (
                      <span className="inline-block mt-1 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Today
                      </span>
                    )}
                  </div>

                  <button
                    onClick={handleNextDay}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>

                <button
                  onClick={handleToday}
                  className="w-full mt-3 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors font-medium"
                >
                  Jump to Today
                </button>
              </div>

              {/* Daily Note Content */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold mb-4">Daily Note</h3>
                <textarea
                  value={editingContent}
                  onChange={(e) => setEditingContent(e.target.value)}
                  placeholder="What's on your mind today? Capture your thoughts, ideas, and reflections..."
                  className="w-full border rounded-lg p-4 min-h-[200px] focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                />
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={handleSaveDailyNote}
                    disabled={isSaving}
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

              {/* Linked Notes */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold flex items-center gap-2">
                    <LinkIcon className="w-5 h-5" />
                    Linked Notes ({linkedNotes.length})
                  </h3>
                  <button
                    onClick={() => setShowLinkModal(true)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 transition-colors text-sm font-medium"
                  >
                    <Plus className="w-4 h-4" />
                    Link Note
                  </button>
                </div>

                {linkedNotes.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No linked notes yet. Link notes to organize related content.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {linkedNotes.map((note) => (
                      <div
                        key={note.id}
                        className="flex items-start justify-between p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{note.title || 'Untitled'}</h4>
                          <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                            {note.content}
                          </p>
                          <span className="inline-block mt-2 text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                            {note.note_type}
                          </span>
                        </div>
                        <button
                          onClick={() => handleUnlinkNote(note.id)}
                          className="ml-3 p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              {showCalendar && (
                <CalendarView
                  selectedDate={selectedDate}
                  datesWithNotes={datesWithNotes}
                  onDateSelect={setSelectedDate}
                />
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Link Note Modal */}
      {showLinkModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-xl font-semibold">Link a Note</h3>
              <button
                onClick={() => setShowLinkModal(false)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {getAvailableNotesToLink().length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No notes available to link. All notes are already linked or you haven't created any notes yet.
                </p>
              ) : (
                <div className="space-y-2">
                  {getAvailableNotesToLink().map((note) => (
                    <button
                      key={note.id}
                      onClick={() => {
                        handleLinkNote(note.id)
                        setShowLinkModal(false)
                      }}
                      className="w-full text-left p-4 border rounded-lg hover:bg-gray-50 hover:border-indigo-300 transition-colors"
                    >
                      <h4 className="font-medium text-gray-900">{note.title || 'Untitled'}</h4>
                      <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                        {note.content}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                          {note.note_type}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(note.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
