import { Extension } from '@tiptap/core'
import { ReactRenderer } from '@tiptap/react'
import Suggestion, { SuggestionOptions } from '@tiptap/suggestion'
import tippy, { Instance as TippyInstance } from 'tippy.js'
import { SlashCommandMenu, SlashCommandMenuRef } from '../components/SlashCommandMenu'
import { Editor } from '@tiptap/react'

interface CommandItem {
  title: string
  description: string
  icon: string
  command: ({ editor, range }: { editor: Editor; range: any }) => void
}

const suggestionItems: CommandItem[] = [
  {
    title: 'Text',
    description: 'Just start writing with plain text.',
    icon: '📝',
    command: ({ editor, range }) => {
      editor
        .chain()
        .focus()
        .deleteRange(range)
        .toggleNode('paragraph', 'paragraph')
        .run()
    }
  },
  {
    title: 'Heading 1',
    description: 'Big section heading.',
    icon: 'H1',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run()
    }
  },
  {
    title: 'Heading 2',
    description: 'Medium section heading.',
    icon: 'H2',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run()
    }
  },
  {
    title: 'Heading 3',
    description: 'Small section heading.',
    icon: 'H3',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run()
    }
  },
  {
    title: 'Bullet List',
    description: 'Create a simple bullet list.',
    icon: '•',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBulletList().run()
    }
  },
  {
    title: 'Numbered List',
    description: 'Create a list with numbering.',
    icon: '1.',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleOrderedList().run()
    }
  },
  {
    title: 'Task List',
    description: 'Track tasks with a checkbox list.',
    icon: '☑',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleTaskList().run()
    }
  },
  {
    title: 'Quote',
    description: 'Capture a quote.',
    icon: '"',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBlockquote().run()
    }
  },
  {
    title: 'Code Block',
    description: 'Capture a code snippet.',
    icon: '</>',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleCodeBlock().run()
    }
  },
  {
    title: 'Table',
    description: 'Insert a table.',
    icon: '⊞',
    command: ({ editor, range }) => {
      editor
        .chain()
        .focus()
        .deleteRange(range)
        .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
        .run()
    }
  },
  {
    title: 'Image',
    description: 'Upload or embed an image.',
    icon: '🖼',
    command: ({ editor, range }) => {
      const url = window.prompt('Enter image URL:')
      if (url) {
        editor.chain().focus().deleteRange(range).setImage({ src: url }).run()
      }
    }
  },
  {
    title: 'Divider',
    description: 'Visually divide blocks.',
    icon: '—',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHorizontalRule().run()
    }
  }
]

export const SlashCommand = Extension.create({
  name: 'slashCommand',

  addOptions() {
    return {
      suggestion: {
        char: '/',
        command: ({ editor, range, props }: { editor: Editor; range: any; props: any }) => {
          props.command({ editor, range })
        }
      } as Partial<SuggestionOptions>
    }
  },

  addProseMirrorPlugins() {
    return [
      Suggestion({
        editor: this.editor,
        ...this.options.suggestion,
        items: ({ query }: { query: string }) => {
          return suggestionItems.filter((item) =>
            item.title.toLowerCase().startsWith(query.toLowerCase())
          )
        },
        render: () => {
          let component: ReactRenderer<SlashCommandMenuRef>
          let popup: TippyInstance[]

          return {
            onStart: (props: any) => {
              component = new ReactRenderer(SlashCommandMenu, {
                props,
                editor: props.editor
              })

              if (!props.clientRect) {
                return
              }

              popup = tippy('body', {
                getReferenceClientRect: props.clientRect,
                appendTo: () => document.body,
                content: component.element,
                showOnCreate: true,
                interactive: true,
                trigger: 'manual',
                placement: 'bottom-start'
              })
            },

            onUpdate(props: any) {
              component.updateProps(props)

              if (!props.clientRect) {
                return
              }

              popup[0].setProps({
                getReferenceClientRect: props.clientRect
              })
            },

            onKeyDown(props: any) {
              if (props.event.key === 'Escape') {
                popup[0].hide()
                return true
              }

              return component.ref?.onKeyDown(props) || false
            },

            onExit() {
              popup[0].destroy()
              component.destroy()
            }
          }
        }
      })
    ]
  }
})
