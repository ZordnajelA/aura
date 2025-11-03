import MDEditor from '@uiw/react-md-editor'
import '@uiw/react-md-editor/markdown-editor.css'

interface MarkdownEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  height?: number
  preview?: 'live' | 'edit' | 'preview'
}

export default function MarkdownEditor({
  value,
  onChange,
  placeholder = 'Start typing...',
  height = 200,
  preview = 'edit'
}: MarkdownEditorProps) {
  return (
    <div data-color-mode="light">
      {/* @ts-ignore - Type mismatch between React versions */}
      <MDEditor
        value={value}
        onChange={(val) => onChange(val || '')}
        preview={preview}
        height={height}
        textareaProps={{
          placeholder: placeholder
        }}
        style={{
          borderRadius: '0.5rem',
          overflow: 'hidden'
        }}
      />
    </div>
  )
}
