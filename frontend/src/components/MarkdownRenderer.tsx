import MarkdownPreview from '@uiw/react-markdown-preview'
import '@uiw/react-markdown-preview/markdown.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  if (!content) {
    return <span className="text-gray-400 italic">No content</span>
  }

  return (
    <div data-color-mode="light" className={className}>
      {/* @ts-ignore - Type mismatch between React versions */}
      <MarkdownPreview
        source={content}
        style={{
          backgroundColor: 'transparent',
          color: 'inherit',
          fontFamily: 'inherit',
          fontSize: 'inherit',
          padding: 0
        }}
        wrapperElement={{
          'data-color-mode': 'light'
        }}
      />
    </div>
  )
}
