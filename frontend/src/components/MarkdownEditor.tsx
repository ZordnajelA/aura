import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { Markdown } from 'tiptap-markdown'
import { useEffect, useState } from 'react'
import './MarkdownEditor.css'

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
  placeholder = 'Start typing...',
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
        placeholder: placeholder
      }),
      Markdown.configure({
        html: false,
        transformPastedText: true,
        transformCopiedText: true
      })
    ],
    content: value,
    editorProps: {
      attributes: {
        class: 'prose prose-sm max-w-none focus:outline-none'
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
    <div className="markdown-editor-container" style={{ height: `${height}px` }}>
      <div className="markdown-editor-toolbar">
        <div className="markdown-editor-toolbar-group">
          <button
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={editor.isActive('bold') ? 'is-active' : ''}
            title="Bold (Ctrl+B)"
            type="button"
          >
            <strong>B</strong>
          </button>
          <button
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={editor.isActive('italic') ? 'is-active' : ''}
            title="Italic (Ctrl+I)"
            type="button"
          >
            <em>I</em>
          </button>
          <button
            onClick={() => editor.chain().focus().toggleStrike().run()}
            className={editor.isActive('strike') ? 'is-active' : ''}
            title="Strikethrough"
            type="button"
          >
            <s>S</s>
          </button>
        </div>

        <div className="markdown-editor-toolbar-group">
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            className={editor.isActive('heading', { level: 1 }) ? 'is-active' : ''}
            title="Heading 1"
            type="button"
          >
            H1
          </button>
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            className={editor.isActive('heading', { level: 2 }) ? 'is-active' : ''}
            title="Heading 2"
            type="button"
          >
            H2
          </button>
          <button
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            className={editor.isActive('heading', { level: 3 }) ? 'is-active' : ''}
            title="Heading 3"
            type="button"
          >
            H3
          </button>
        </div>

        <div className="markdown-editor-toolbar-group">
          <button
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={editor.isActive('bulletList') ? 'is-active' : ''}
            title="Bullet List"
            type="button"
          >
            • List
          </button>
          <button
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={editor.isActive('orderedList') ? 'is-active' : ''}
            title="Numbered List"
            type="button"
          >
            1. List
          </button>
          <button
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            className={editor.isActive('blockquote') ? 'is-active' : ''}
            title="Blockquote"
            type="button"
          >
            " Quote
          </button>
          <button
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            className={editor.isActive('codeBlock') ? 'is-active' : ''}
            title="Code Block"
            type="button"
          >
            {'<>'} Code
          </button>
        </div>

        <div className="markdown-editor-toolbar-group">
          <button
            onClick={() => setShowSource(!showSource)}
            className={showSource ? 'is-active' : ''}
            title="Toggle Markdown Source"
            type="button"
          >
            {showSource ? '👁️ View' : '📝 Source'}
          </button>
        </div>
      </div>

      {showSource ? (
        <textarea
          className="markdown-editor-source"
          value={sourceValue}
          onChange={(e) => handleSourceChange(e.target.value)}
          onBlur={handleSourceBlur}
          style={{
            height: `${height - 45}px`,
            fontFamily: 'monospace',
            fontSize: '14px',
            padding: '12px',
            border: '1px solid #e5e7eb',
            borderRadius: '0 0 0.5rem 0.5rem',
            width: '100%',
            resize: 'none',
            outline: 'none'
          }}
        />
      ) : (
        <EditorContent
          editor={editor}
          className="markdown-editor-content"
          style={{ height: `${height - 45}px` }}
        />
      )}
    </div>
  )
}
