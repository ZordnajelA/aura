import { Editor } from '@tiptap/react'
import { useEffect, useRef, useState } from 'react'
import tippy, { Instance as TippyInstance } from 'tippy.js'
import './BubbleMenu.css'

interface BubbleMenuProps {
  editor: Editor
}

const TEXT_COLORS = ['#000000', '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899']
const HIGHLIGHT_COLORS = ['transparent', '#fef3c7', '#fed7aa', '#fecaca', '#d9f99d', '#bfdbfe', '#ddd6fe', '#fbcfe8']
const FONT_SIZES = ['12px', '14px', '16px', '18px', '20px', '24px', '32px', '48px']

export default function BubbleMenu({ editor }: BubbleMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)
  const tippyInstanceRef = useRef<TippyInstance | null>(null)
  const [showColorPicker, setShowColorPicker] = useState(false)
  const [showHighlightPicker, setShowHighlightPicker] = useState(false)
  const [showFontSizePicker, setShowFontSizePicker] = useState(false)

  useEffect(() => {
    if (!menuRef.current) return

    const updateMenu = () => {
      const { state } = editor
      const { selection } = state
      const { empty } = selection

      if (empty) {
        tippyInstanceRef.current?.hide()
        return
      }

      if (!tippyInstanceRef.current) {
        tippyInstanceRef.current = tippy(document.body, {
          getReferenceClientRect: () => {
            const { ranges } = selection
            const from = Math.min(...ranges.map((range) => range.$from.pos))

            return editor.view.coordsAtPos(from) as DOMRect
          },
          appendTo: () => document.body,
          content: menuRef.current!,
          showOnCreate: true,
          interactive: true,
          trigger: 'manual',
          placement: 'top',
          arrow: false
        })
      }

      tippyInstanceRef.current.show()
    }

    editor.on('selectionUpdate', updateMenu)
    editor.on('update', updateMenu)

    return () => {
      editor.off('selectionUpdate', updateMenu)
      editor.off('update', updateMenu)
      tippyInstanceRef.current?.destroy()
    }
  }, [editor])

  return (
    <div ref={menuRef} className="bubble-menu">
      <div className="bubble-menu-content">
        {/* Text Formatting */}
        <button
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'active' : ''}
          title="Bold (Ctrl+B)"
        >
          <strong>B</strong>
        </button>

        <button
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'active' : ''}
          title="Italic (Ctrl+I)"
        >
          <em>I</em>
        </button>

        <button
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          className={editor.isActive('underline') ? 'active' : ''}
          title="Underline (Ctrl+U)"
        >
          <u>U</u>
        </button>

        <button
          onClick={() => editor.chain().focus().toggleStrike().run()}
          className={editor.isActive('strike') ? 'active' : ''}
          title="Strikethrough"
        >
          <s>S</s>
        </button>

        <button
          onClick={() => editor.chain().focus().toggleCode().run()}
          className={editor.isActive('code') ? 'active' : ''}
          title="Inline Code"
        >
          {'</>'}
        </button>

        <div className="bubble-menu-divider" />

        {/* Superscript / Subscript */}
        <button
          onClick={() => editor.chain().focus().toggleSuperscript().run()}
          className={editor.isActive('superscript') ? 'active' : ''}
          title="Superscript"
        >
          x<sup>2</sup>
        </button>

        <button
          onClick={() => editor.chain().focus().toggleSubscript().run()}
          className={editor.isActive('subscript') ? 'active' : ''}
          title="Subscript"
        >
          x<sub>2</sub>
        </button>

        <div className="bubble-menu-divider" />

        {/* Text Color */}
        <div className="bubble-menu-dropdown">
          <button
            onClick={() => {
              setShowColorPicker(!showColorPicker)
              setShowHighlightPicker(false)
              setShowFontSizePicker(false)
            }}
            title="Text Color"
            className="color-button"
          >
            A
            <span className="color-indicator" style={{ backgroundColor: editor.getAttributes('textStyle').color || '#000000' }} />
          </button>
          {showColorPicker && (
            <div className="bubble-menu-picker">
              {TEXT_COLORS.map(color => (
                <button
                  key={color}
                  className="color-swatch"
                  style={{ backgroundColor: color }}
                  onClick={() => {
                    editor.chain().focus().setColor(color).run()
                    setShowColorPicker(false)
                  }}
                  title={color}
                />
              ))}
            </div>
          )}
        </div>

        {/* Highlight */}
        <div className="bubble-menu-dropdown">
          <button
            onClick={() => {
              setShowHighlightPicker(!showHighlightPicker)
              setShowColorPicker(false)
              setShowFontSizePicker(false)
            }}
            title="Highlight"
            className="color-button"
          >
            <span style={{ backgroundColor: '#fef3c7', padding: '0 4px' }}>H</span>
          </button>
          {showHighlightPicker && (
            <div className="bubble-menu-picker">
              {HIGHLIGHT_COLORS.map(color => (
                <button
                  key={color}
                  className="color-swatch"
                  style={{
                    backgroundColor: color,
                    border: color === 'transparent' ? '1px solid #e5e7eb' : 'none'
                  }}
                  onClick={() => {
                    if (color === 'transparent') {
                      editor.chain().focus().unsetHighlight().run()
                    } else {
                      editor.chain().focus().setHighlight({ color }).run()
                    }
                    setShowHighlightPicker(false)
                  }}
                  title={color === 'transparent' ? 'Remove highlight' : color}
                />
              ))}
            </div>
          )}
        </div>

        <div className="bubble-menu-divider" />

        {/* Font Size */}
        <div className="bubble-menu-dropdown">
          <button
            onClick={() => {
              setShowFontSizePicker(!showFontSizePicker)
              setShowColorPicker(false)
              setShowHighlightPicker(false)
            }}
            title="Font Size"
            className="text-size-button"
          >
            Size
          </button>
          {showFontSizePicker && (
            <div className="bubble-menu-picker size-picker">
              {FONT_SIZES.map(size => (
                <button
                  key={size}
                  className="size-option"
                  onClick={() => {
                    editor.chain().focus().setMark('textStyle', { fontSize: size }).run()
                    setShowFontSizePicker(false)
                  }}
                >
                  {size}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="bubble-menu-divider" />

        {/* Alignment */}
        <button
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          className={editor.isActive({ textAlign: 'left' }) ? 'active' : ''}
          title="Align Left"
        >
          ⬅
        </button>

        <button
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          className={editor.isActive({ textAlign: 'center' }) ? 'active' : ''}
          title="Align Center"
        >
          ↔
        </button>

        <button
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          className={editor.isActive({ textAlign: 'right' }) ? 'active' : ''}
          title="Align Right"
        >
          ➡
        </button>

        <button
          onClick={() => editor.chain().focus().setTextAlign('justify').run()}
          className={editor.isActive({ textAlign: 'justify' }) ? 'active' : ''}
          title="Justify"
        >
          ≡
        </button>
      </div>
    </div>
  )
}
