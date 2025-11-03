import { useState, useRef } from 'react'
import { Paperclip, Send, Link as LinkIcon } from 'lucide-react'
import MarkdownEditor from './MarkdownEditor'
import notesService from '../services/notes'
import dailyNotesService from '../services/daily_notes'

export default function CaptureInterface() {
  const [input, setInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [autoLinkToDaily, setAutoLinkToDaily] = useState(true)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isSubmitting) return

    setIsSubmitting(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await notesService.createNote({
        content: input.trim(),
        note_type: 'text'
      })
      console.log('Note created:', response)

      // Auto-link to today's daily note if enabled
      if (autoLinkToDaily) {
        try {
          await dailyNotesService.linkNoteToToday(response.id)
          setSuccessMessage(`✓ Note created and linked to today's daily note`)
        } catch (linkErr) {
          console.error('Error linking to daily note:', linkErr)
          setSuccessMessage(`✓ Note created (linking failed)`)
        }
      } else {
        setSuccessMessage(`✓ Note created successfully`)
      }

      setInput('')

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      console.error('Error creating note:', err)
      setError('Failed to create note. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setError(null)
    setSuccessMessage(null)

    for (const file of Array.from(files)) {
      try {
        // Determine note type based on file type
        let noteType = 'file'
        if (file.type.startsWith('image/')) noteType = 'image'
        else if (file.type.startsWith('audio/')) noteType = 'audio'
        else if (file.type.startsWith('video/')) noteType = 'video'
        else if (file.type === 'application/pdf') noteType = 'pdf'

        // For now, create a note with file information
        // TODO: Implement full file upload with media service
        const response = await notesService.createNote({
          title: file.name,
          content: `File upload placeholder: ${file.name} (${file.type}, ${(file.size / 1024).toFixed(2)} KB)`,
          note_type: noteType
        })
        console.log('File note created:', response)

        // Auto-link to today's daily note if enabled
        if (autoLinkToDaily) {
          try {
            await dailyNotesService.linkNoteToToday(response.id)
            setSuccessMessage(`✓ File "${file.name}" note created and linked to today`)
          } catch (linkErr) {
            console.error('Error linking file to daily note:', linkErr)
            setSuccessMessage(`✓ File "${file.name}" note created (linking failed)`)
          }
        } else {
          setSuccessMessage(`✓ File "${file.name}" note created`)
        }

        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        console.error('Error creating file note:', err)
        setError(`Failed to create note for file "${file.name}". Please try again.`)
      }
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleClipClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto p-4">
      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        <div className="text-center text-gray-500 py-8">
          <p className="text-lg">Start capturing your thoughts, files, or links</p>
          <p className="text-sm mt-2">Type or paste anything, or click the paperclip to upload files</p>
        </div>

        {/* Status messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {successMessage}
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileSelect}
        className="hidden"
        aria-label="File upload input"
      />

      {/* Input area */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-4">
        {/* Auto-link toggle */}
        <div className="flex items-center gap-2 mb-3 text-sm">
          <input
            type="checkbox"
            id="autoLinkToDaily"
            checked={autoLinkToDaily}
            onChange={(e) => setAutoLinkToDaily(e.target.checked)}
            className="rounded border-gray-300 text-primary-500 focus:ring-primary-500"
          />
          <label htmlFor="autoLinkToDaily" className="flex items-center gap-1 text-gray-700 cursor-pointer">
            <LinkIcon className="w-4 h-4" />
            Auto-link to today's daily note
          </label>
        </div>

        <div className="space-y-3">
          <div className="flex-1">
            <MarkdownEditor
              value={input}
              onChange={setInput}
              placeholder="Capture anything: text, ideas, tasks...

**Supports markdown:**
- **Bold**, *italic*, `code`
- Lists and [links](url)"
              height={150}
              preview="edit"
            />
          </div>

          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={handleClipClick}
              className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors text-sm text-gray-700"
              aria-label="Attach file"
            >
              <Paperclip className="w-4 h-4" />
              Attach File
            </button>

            <button
              type="submit"
              disabled={!input.trim() || isSubmitting}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Send"
            >
              {isSubmitting ? (
                'Saving...'
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Capture
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
