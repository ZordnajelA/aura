import { useState } from 'react'
import { Paperclip, Send } from 'lucide-react'

export default function CaptureInterface() {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    // TODO: Send to backend
    console.log('Captured:', input)
    setInput('')
  }

  return (
    <div className="h-full flex flex-col max-w-4xl mx-auto p-4">
      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        <div className="text-center text-gray-500 py-8">
          <p className="text-lg">Start capturing your thoughts, files, or links</p>
          <p className="text-sm mt-2">Type or paste anything, or click the paperclip to upload files</p>
        </div>
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-4">
        <div className="flex items-end gap-2">
          <button
            type="button"
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
            disabled={!input.trim()}
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
