import { Editor } from '@tiptap/react'
import { useEffect, useRef, useState } from 'react'
import './FloatingMenu.css'

interface FloatingMenuProps {
  editor: Editor
}

export default function FloatingMenu({ editor }: FloatingMenuProps) {
  const [showMenu, setShowMenu] = useState(false)
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 })
  const menuRef = useRef<HTMLDivElement>(null)
  const [hoveredBlock, setHoveredBlock] = useState<HTMLElement | null>(null)

  useEffect(() => {
    const editorElement = editor.view.dom

    const handleMouseMove = (e: MouseEvent) => {
      const target = e.target as HTMLElement

      // Find the closest block-level element
      const blockElement = target.closest('p, h1, h2, h3, h4, h5, h6, li, blockquote, pre, table') as HTMLElement

      if (blockElement && editorElement.contains(blockElement)) {
        setHoveredBlock(blockElement)

        const rect = blockElement.getBoundingClientRect()
        const editorRect = editorElement.getBoundingClientRect()

        setMenuPosition({
          top: rect.top - editorRect.top,
          left: -60 // Position to the left of the block
        })
        setShowMenu(true)
      } else {
        setShowMenu(false)
        setHoveredBlock(null)
      }
    }

    const handleMouseLeave = () => {
      // Don't hide if hovering over the menu itself
      setTimeout(() => {
        if (!menuRef.current?.matches(':hover')) {
          setShowMenu(false)
          setHoveredBlock(null)
        }
      }, 100)
    }

    editorElement.addEventListener('mousemove', handleMouseMove)
    editorElement.addEventListener('mouseleave', handleMouseLeave)

    return () => {
      editorElement.removeEventListener('mousemove', handleMouseMove)
      editorElement.removeEventListener('mouseleave', handleMouseLeave)
    }
  }, [editor])

  const handleDragStart = (e: React.DragEvent) => {
    if (!hoveredBlock) return

    // Set drag data
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/html', hoveredBlock.outerHTML)

    // Add dragging class
    hoveredBlock.classList.add('dragging')
  }

  const handleDragEnd = () => {
    if (hoveredBlock) {
      hoveredBlock.classList.remove('dragging')
    }
  }

  const handleAddBlock = () => {
    if (!hoveredBlock) return

    // Get the position after the current block
    const pos = editor.view.posAtDOM(hoveredBlock, 0)
    const $pos = editor.state.doc.resolve(pos)
    const after = $pos.after()

    // Set cursor position and trigger slash command
    editor.chain().focus().setTextSelection(after).run()

    // Insert a new paragraph and trigger the slash command
    editor.chain().insertContentAt(after, { type: 'paragraph' }).setTextSelection(after + 1).run()

    // Simulate typing "/" to trigger slash menu
    editor.commands.insertContent('/')
  }

  if (!showMenu) return null

  return (
    <div
      ref={menuRef}
      className="floating-menu"
      style={{
        top: `${menuPosition.top}px`,
        left: `${menuPosition.left}px`
      }}
    >
      <button
        className="floating-menu-button drag-handle"
        draggable
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        title="Drag to move"
      >
        ⋮⋮
      </button>
      <button
        className="floating-menu-button add-button"
        onClick={handleAddBlock}
        title="Add block"
      >
        +
      </button>
    </div>
  )
}
