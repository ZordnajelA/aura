import { useState, useRef } from 'react'
import { Paperclip, Send } from 'lucide-react'
import { captureText, captureFile } from '../services/capture'

export default function CaptureInterface() {
  const [input, setInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isSubmitting) return

    setIsSubmitting(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await captureText(input.trim())
      console.log('Captured:', response)
      setSuccessMessage(`✓ Captured successfully`)
      setInput('')

      // Clear success message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      console.error('Error capturing text:', err)
      setError('Failed to capture. Please try again.')
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
        const response = await captureFile(file)
        console.log('File captured:', response)
        setSuccessMessage(`✓ File "${file.name}" captured successfully`)

        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        console.error('Error capturing file:', err)
        setError(`Failed to capture file "${file.name}". Please try again.`)
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
        <div className="flex items-end gap-2">
          <button
            type="button"
            onClick={handleClipClick}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Attach file"
          >
            <Paperclip className="w-5 h-5 text-gray-600" />
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Capture anything: text, ideas, tasks, or paste a link..."
            className="flex-1 resize-none border-0 focus:ring-0 focus:outline-none max-h-32"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          />

          <button
            type="submit"
            disabled={!input.trim() || isSubmitting}
            className="p-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  )
}
