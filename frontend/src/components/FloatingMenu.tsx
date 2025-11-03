import { Editor } from '@tiptap/react'
import { useEffect, useRef } from 'react'
import './FloatingMenu.css'

interface FloatingMenuProps {
  editor: Editor
}

export default function FloatingMenu({ editor }: FloatingMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const editorElement = editor.view.dom.parentElement

    if (!editorElement || !menuRef.current) return

    const menu = menuRef.current

    let currentBlock: HTMLElement | null = null
    let rafId: number

    const updateMenuPosition = (blockElement: HTMLElement) => {
      const blockRect = blockElement.getBoundingClientRect()
      const editorRect = editorElement.getBoundingClientRect()

      menu.style.display = 'flex'
      menu.style.top = `${blockRect.top - editorRect.top + editorElement.scrollTop}px`
      menu.style.left = `-50px`
    }

    const hideMenu = () => {
      menu.style.display = 'none'
      currentBlock = null
    }

    const handleMouseMove = (e: MouseEvent) => {
      if (rafId) {
        cancelAnimationFrame(rafId)
      }

      rafId = requestAnimationFrame(() => {
        const target = e.target as HTMLElement

        // Find the closest block-level element within the ProseMirror editor
        const proseMirror = editorElement.querySelector('.ProseMirror')
        if (!proseMirror || !proseMirror.contains(target)) {
          hideMenu()
          return
        }

        // Find the closest block element
        let blockElement = target.closest('p, h1, h2, h3, h4, h5, h6, li, blockquote, pre, tr') as HTMLElement

        // For list items, use the list item itself, not the list
        if (blockElement && blockElement.tagName === 'LI') {
          // Keep as is
        } else if (blockElement && blockElement.tagName === 'TR') {
          // For table rows, use the row
        } else if (!blockElement) {
          // If no block element found, try to find a direct child of ProseMirror
          let node = target
          while (node && node.parentElement !== proseMirror) {
            node = node.parentElement as HTMLElement
          }
          if (node && proseMirror.contains(node)) {
            blockElement = node as HTMLElement
          }
        }

        if (blockElement && proseMirror.contains(blockElement)) {
          if (blockElement !== currentBlock) {
            currentBlock = blockElement
            currentBlock.setAttribute('data-block-hovered', 'true')
            updateMenuPosition(blockElement)
          }
        } else {
          hideMenu()
        }
      })
    }

    const handleMouseLeave = () => {
      setTimeout(() => {
        if (!menu.matches(':hover')) {
          hideMenu()
        }
      }, 100)
    }

    const handleDragStart = (e: DragEvent) => {
      if (!currentBlock) return
      e.dataTransfer!.effectAllowed = 'move'
      currentBlock.classList.add('dragging')
    }

    const handleDragEnd = () => {
      if (currentBlock) {
        currentBlock.classList.remove('dragging')
      }
    }

    const handleAddClick = () => {
      if (!currentBlock) return

      // Get the position after the current block
      const pos = editor.view.posAtDOM(currentBlock, 0)
      const $pos = editor.state.doc.resolve(pos)
      const after = $pos.after()

      // Insert a new paragraph and add /
      editor.chain()
        .focus()
        .insertContentAt(after, { type: 'paragraph' })
        .setTextSelection(after + 1)
        .insertContent('/')
        .run()
    }

    // Attach event listeners
    editorElement.addEventListener('mousemove', handleMouseMove)
    editorElement.addEventListener('mouseleave', handleMouseLeave)

    const dragHandle = menu.querySelector('.drag-handle')
    const addButton = menu.querySelector('.add-button')

    if (dragHandle) {
      dragHandle.addEventListener('dragstart', handleDragStart as any)
      dragHandle.addEventListener('dragend', handleDragEnd)
    }

    if (addButton) {
      addButton.addEventListener('click', handleAddClick)
    }

    return () => {
      if (rafId) {
        cancelAnimationFrame(rafId)
      }
      editorElement.removeEventListener('mousemove', handleMouseMove)
      editorElement.removeEventListener('mouseleave', handleMouseLeave)

      if (dragHandle) {
        dragHandle.removeEventListener('dragstart', handleDragStart as any)
        dragHandle.removeEventListener('dragend', handleDragEnd)
      }

      if (addButton) {
        addButton.removeEventListener('click', handleAddClick)
      }
    }
  }, [editor])

  return (
    <div ref={menuRef} className="floating-menu">
      <button
        className="floating-menu-button drag-handle"
        draggable
        title="Drag to move"
        type="button"
      >
        ⋮⋮
      </button>
      <button
        className="floating-menu-button add-button"
        title="Add block"
        type="button"
      >
        +
      </button>
    </div>
  )
}
