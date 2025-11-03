import { Editor } from '@tiptap/react'
import { useState, useEffect } from 'react'
import './TableOfContents.css'

interface TableOfContentsProps {
  editor: Editor
}

interface Heading {
  level: number
  text: string
  id: string
}

export default function TableOfContents({ editor }: TableOfContentsProps) {
  const [headings, setHeadings] = useState<Heading[]>([])
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const updateHeadings = () => {
      const newHeadings: Heading[] = []
      const json = editor.getJSON()

      const extractHeadings = (node: any) => {
        if (node.type === 'heading') {
          const text = node.content?.map((n: any) => n.text).join('') || ''
          newHeadings.push({
            level: node.attrs.level,
            text: text,
            id: `heading-${newHeadings.length}`
          })
        }
        if (node.content) {
          node.content.forEach(extractHeadings)
        }
      }

      if (json.content) {
        json.content.forEach(extractHeadings)
      }

      setHeadings(newHeadings)
    }

    updateHeadings()
    editor.on('update', updateHeadings)

    return () => {
      editor.off('update', updateHeadings)
    }
  }, [editor])

  const scrollToHeading = (text: string) => {
    // Find the heading in the editor and scroll to it
    const editorElement = editor.view.dom
    const walker = document.createTreeWalker(
      editorElement,
      NodeFilter.SHOW_ELEMENT,
      {
        acceptNode: (node) => {
          const el = node as HTMLElement
          return (el.tagName.match(/^H[1-6]$/) && el.textContent === text)
            ? NodeFilter.FILTER_ACCEPT
            : NodeFilter.FILTER_SKIP
        }
      }
    )

    const headingElement = walker.nextNode() as HTMLElement
    if (headingElement) {
      headingElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setIsOpen(false)
    }
  }

  return (
    <div className="table-of-contents">
      <button
        className="toc-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title="Table of Contents"
      >
        ☰
      </button>

      {isOpen && (
        <>
          <div className="toc-overlay" onClick={() => setIsOpen(false)} />
          <div className="toc-panel">
            <div className="toc-header">
              <h3>Table of Contents</h3>
              <button
                className="toc-close"
                onClick={() => setIsOpen(false)}
              >
                ✕
              </button>
            </div>
            <div className="toc-content">
              {headings.length === 0 ? (
                <div className="toc-empty">No headings yet</div>
              ) : (
                <ul className="toc-list">
                  {headings.map((heading, index) => (
                    <li
                      key={index}
                      className={`toc-item level-${heading.level}`}
                      onClick={() => scrollToHeading(heading.text)}
                    >
                      {heading.text}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
