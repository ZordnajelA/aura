import { useState, useEffect } from 'react'
import { FileText, Image, FileAudio, FileVideo, File, Link2, Loader2, Trash2, Edit, Search, Filter } from 'lucide-react'
import Navigation from '@/components/Navigation'
import MarkdownEditor from '@/components/MarkdownEditor'
import MarkdownRenderer from '@/components/MarkdownRenderer'
import AIResultDisplay from '@/components/AIResultDisplay'
import notesService, { Note } from '@/services/notes'
import processingService from '@/services/processing'
import type { TextClassification, ProcessedContent } from '@/types'

const NOTE_TYPE_ICONS = {
  text: FileText,
  image: Image,
  audio: FileAudio,
  video: FileVideo,
  pdf: File,
  link: Link2,
  file: File,
}

const NOTE_TYPE_COLORS = {
  text: 'bg-blue-100 text-blue-700',
  image: 'bg-green-100 text-green-700',
  audio: 'bg-purple-100 text-purple-700',
  video: 'bg-red-100 text-red-700',
  pdf: 'bg-orange-100 text-orange-700',
  link: 'bg-cyan-100 text-cyan-700',
  file: 'bg-gray-100 text-gray-700',
}

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [filterType, setFilterType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadNotes()
  }, [])

  const loadNotes = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const fetchedNotes = await notesService.getNotes(0, 100)
      setNotes(fetchedNotes)
    } catch (err) {
      console.error('Error loading notes:', err)
      setError('Failed to load notes')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteNote = async (noteId: string, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent opening the note detail
    if (!confirm('Are you sure you want to delete this note?')) return

    try {
      await notesService.deleteNote(noteId)
      setNotes(notes.filter(note => note.id !== noteId))
      if (selectedNote?.id === noteId) {
        setSelectedNote(null)
      }
    } catch (err) {
      console.error('Error deleting note:', err)
      setError('Failed to delete note')
    }
  }

  const handleUpdateNote = async (noteId: string, title: string, content: string) => {
    try {
      const updatedNote = await notesService.updateNote(noteId, { title, content })
      setNotes(notes.map(note => note.id === noteId ? updatedNote : note))
      setSelectedNote(updatedNote)
      setIsEditing(false)
    } catch (err) {
      console.error('Error updating note:', err)
      setError('Failed to update note')
    }
  }

  const filteredNotes = notes.filter(note => {
    // Filter by type
    if (filterType !== 'all' && note.note_type !== filterType) return false

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      return (
        note.title?.toLowerCase().includes(query) ||
        note.content?.toLowerCase().includes(query)
      )
    }

    return true
  })

  const noteTypes = ['all', ...Array.from(new Set(notes.map(note => note.note_type)))]

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getNoteIcon = (noteType: string) => {
    const Icon = NOTE_TYPE_ICONS[noteType as keyof typeof NOTE_TYPE_ICONS] || FileText
    return Icon
  }

  const getNoteColor = (noteType: string) => {
    return NOTE_TYPE_COLORS[noteType as keyof typeof NOTE_TYPE_COLORS] || 'bg-gray-100 text-gray-700'
  }

  return (
    <div className="h-screen flex flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto bg-gray-50">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <FileText className="w-8 h-8" />
              All Notes
            </h1>
            <div className="text-sm text-gray-500">
              {filteredNotes.length} {filteredNotes.length === 1 ? 'note' : 'notes'}
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <div className="flex gap-4 items-center">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search notes by title or content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              {/* Filter by Type */}
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-500" />
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {noteTypes.map(type => (
                    <option key={type} value={type}>
                      {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
            </div>
          ) : filteredNotes.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow-md">
              <FileText className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">
                {searchQuery || filterType !== 'all'
                  ? 'No notes found matching your filters'
                  : 'No notes yet. Start capturing on the home page!'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredNotes.map((note) => {
                const Icon = getNoteIcon(note.note_type)
                return (
                  <div
                    key={note.id}
                    onClick={() => {
                      setSelectedNote(note)
                      setIsEditing(false)
                    }}
                    className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow cursor-pointer"
                  >
                    {/* Note Type Badge */}
                    <div className="flex items-center justify-between mb-3">
                      <div className={`flex items-center gap-2 px-2 py-1 rounded text-xs font-medium ${getNoteColor(note.note_type)}`}>
                        <Icon className="w-4 h-4" />
                        {note.note_type}
                      </div>
                      <button
                        onClick={(e) => handleDeleteNote(note.id, e)}
                        className="p-1 hover:bg-red-50 rounded text-red-500 transition-colors"
                        aria-label="Delete note"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Title */}
                    {note.title && (
                      <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
                        {note.title}
                      </h3>
                    )}

                    {/* Content Preview */}
                    {note.content && (
                      <p className="text-gray-600 text-sm line-clamp-3 mb-3">
                        {note.content}
                      </p>
                    )}

                    {/* Date */}
                    <div className="text-xs text-gray-500 mt-auto">
                      {formatDate(note.created_at)}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </main>

      {/* Note Detail Modal */}
      {selectedNote && (
        <NoteDetailModal
          note={selectedNote}
          isEditing={isEditing}
          onClose={() => {
            setSelectedNote(null)
            setIsEditing(false)
          }}
          onEdit={() => setIsEditing(true)}
          onSave={handleUpdateNote}
          onDelete={(noteId) => {
            handleDeleteNote(noteId, { stopPropagation: () => {} } as React.MouseEvent)
            setSelectedNote(null)
          }}
        />
      )}
    </div>
  )
}

// Note Detail Modal Component
interface NoteDetailModalProps {
  note: Note
  isEditing: boolean
  onClose: () => void
  onEdit: () => void
  onSave: (noteId: string, title: string, content: string) => void
  onDelete: (noteId: string) => void
}

function NoteDetailModal({ note, isEditing, onClose, onEdit, onSave, onDelete }: NoteDetailModalProps) {
  const [editTitle, setEditTitle] = useState(note.title || '')
  const [editContent, setEditContent] = useState(note.content || '')
  const [classification, setClassification] = useState<TextClassification | null>(null)
  const [processedContent, setProcessedContent] = useState<ProcessedContent | null>(null)
  const [isLoadingAI, setIsLoadingAI] = useState(false)

  useEffect(() => {
    setEditTitle(note.title || '')
    setEditContent(note.content || '')

    // Load AI results for this note
    loadAIResults()
  }, [note])

  const loadAIResults = async () => {
    setIsLoadingAI(true)
    try {
      // Fetch classification
      const classificationResult = await processingService.getClassification(note.id)
      setClassification(classificationResult)

      // Fetch processed content (for media files)
      const processedResults = await processingService.getProcessingResults(note.id)
      if (processedResults.length > 0) {
        setProcessedContent(processedResults[0]) // Use the first result
      }
    } catch (err) {
      console.error('Error loading AI results:', err)
      // Silent fail - AI results are optional
    } finally {
      setIsLoadingAI(false)
    }
  }

  const handleSave = () => {
    onSave(note.id, editTitle, editContent)
  }

  const Icon = NOTE_TYPE_ICONS[note.note_type as keyof typeof NOTE_TYPE_ICONS] || FileText

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="bg-gray-50 px-6 py-4 border-b flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded ${NOTE_TYPE_COLORS[note.note_type as keyof typeof NOTE_TYPE_COLORS] || 'bg-gray-100 text-gray-700'}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Note Details</h2>
              <p className="text-sm text-gray-500">Created {new Date(note.created_at).toLocaleDateString()}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!isEditing && (
              <button
                onClick={onEdit}
                className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
            )}
            <button
              onClick={() => {
                if (confirm('Are you sure you want to delete this note?')) {
                  onDelete(note.id)
                }
              }}
              className="flex items-center gap-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
            <button
              onClick={onClose}
              className="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-8rem)]">
          {isEditing ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Note title (optional)"
                  className="w-full border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Content</label>
                <MarkdownEditor
                  value={editContent}
                  onChange={setEditContent}
                  placeholder="Note content - supports markdown formatting"
                  height={400}
                  preview="edit"
                />
              </div>
              <div className="flex justify-end gap-2 pt-4 border-t">
                <button
                  onClick={() => {
                    setEditTitle(note.title || '')
                    setEditContent(note.content || '')
                    onEdit()
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  Save Changes
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {note.title && (
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">{note.title}</h3>
                </div>
              )}

              {/* AI Results Section */}
              {(classification || processedContent) && (
                <AIResultDisplay
                  classification={classification}
                  processedContent={processedContent}
                />
              )}

              {isLoadingAI && !classification && !processedContent && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-2 text-blue-700">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Loading AI analysis...</span>
                </div>
              )}

              <div className="prose max-w-none">
                <MarkdownRenderer content={note.content || ''} className="text-gray-700" />
              </div>
              <div className="pt-4 border-t text-sm text-gray-500">
                <p>Last updated: {new Date(note.updated_at).toLocaleString()}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
