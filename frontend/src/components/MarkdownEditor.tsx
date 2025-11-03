import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { Markdown } from 'tiptap-markdown'
import { SlashCommand } from '../extensions/SlashCommand'
import { useEffect, useState } from 'react'
import './MarkdownEditor.css'
import 'tippy.js/dist/tippy.css'

interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  height?: number
  preview?: 'live' | 'edit' | 'preview' // Kept for backwards compatibility
}

export default function MarkdownEditor({
  value,
  onChange,
  placeholder = "Type '/' for commands...",
  height = 200,
  preview: _preview = 'edit' // Kept for backwards compatibility
}: MarkdownEditorProps) {
  const [showSource, setShowSource] = useState(false)
  const [sourceValue, setSourceValue] = useState(value)

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3, 4, 5, 6]
        }
      }),
      Placeholder.configure({
        placeholder: placeholder,
        showOnlyWhenEditable: true,
        showOnlyCurrent: false
      }),
      Markdown.configure({
        html: false,
        transformPastedText: true,
        transformCopiedText: true
      }),
      SlashCommand
    ],
    content: value,
    editorProps: {
      attributes: {
        class: 'block-editor-content'
      }
    },
    onUpdate: ({ editor }) => {
      // @ts-ignore - markdown storage is added by the Markdown extension
      const markdown = editor.storage.markdown.getMarkdown()
      onChange(markdown)
    }
  })

  // Update editor content when value changes externally
  useEffect(() => {
    if (editor) {
      // @ts-ignore - markdown storage is added by the Markdown extension
      const currentMarkdown = editor.storage.markdown.getMarkdown()
      if (value !== currentMarkdown) {
        editor.commands.setContent(value)
      }
    }
  }, [value, editor])

  // Update source value when switching to source mode
  useEffect(() => {
    if (showSource && editor) {
      // @ts-ignore - markdown storage is added by the Markdown extension
      setSourceValue(editor.storage.markdown.getMarkdown())
    }
  }, [showSource, editor])

  const handleSourceChange = (newValue: string) => {
    setSourceValue(newValue)
  }

  const handleSourceBlur = () => {
    if (editor) {
      editor.commands.setContent(sourceValue)
      onChange(sourceValue)
    }
  }

  if (!editor) {
    return null
  }

  return (
    <div className="block-editor-container" style={{ height: `${height}px` }}>
      <div className="block-editor-header">
        <button
          onClick={() => setShowSource(!showSource)}
          className={`source-toggle ${showSource ? 'active' : ''}`}
          title="Toggle Markdown Source"
          type="button"
        >
          {showSource ? '👁️ View' : '📝 Source'}
        </button>
      </div>

      {showSource ? (
        <textarea
          className="block-editor-source"
          value={sourceValue}
          onChange={(e) => handleSourceChange(e.target.value)}
          onBlur={handleSourceBlur}
          style={{
            height: `${height - 40}px`
          }}
        />
      ) : (
        <div className="block-editor-wrapper" style={{ height: `${height - 40}px` }}>
          <EditorContent editor={editor} />
        </div>
      )}
    </div>
  )
}
