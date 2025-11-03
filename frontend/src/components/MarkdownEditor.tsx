import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { Markdown } from 'tiptap-markdown'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { Table } from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import { Color } from '@tiptap/extension-color'
import { TextStyle } from '@tiptap/extension-text-style'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import Image from '@tiptap/extension-image'
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import FontFamily from '@tiptap/extension-font-family'
import Dropcursor from '@tiptap/extension-dropcursor'
import { FontSize } from '../extensions/FontSize'
import { SlashCommand } from '../extensions/SlashCommand'
import BubbleMenu from './BubbleMenu'
import FloatingMenu from './FloatingMenu'
import { useEffect } from 'react'
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
      SlashCommand,
      TaskList,
      TaskItem.configure({
        nested: true
      }),
      Table.configure({
        resizable: true
      }),
      TableRow,
      TableCell,
      TableHeader,
      TextStyle,
      FontSize,
      Color,
      Highlight.configure({
        multicolor: true
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph']
      }),
      Underline,
      Image.configure({
        inline: true,
        allowBase64: true
      }),
      Subscript,
      Superscript,
      FontFamily,
      Dropcursor
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

  if (!editor) {
    return null
  }

  return (
    <div className="block-editor-container" style={{ height: `${height}px` }}>
      <BubbleMenu editor={editor} />
      <FloatingMenu editor={editor} />
      <div className="block-editor-wrapper" style={{ height: `${height}px` }}>
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}
