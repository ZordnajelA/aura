import { forwardRef, useEffect, useImperativeHandle, useState } from 'react'
import './SlashCommandMenu.css'

interface Command {
  title: string
  description: string
  icon: string
  command: () => void
}

interface SlashCommandMenuProps {
  items: Command[]
  command: (item: Command) => void
}

export interface SlashCommandMenuRef {
  onKeyDown: (props: { event: KeyboardEvent }) => boolean
}

export const SlashCommandMenu = forwardRef<SlashCommandMenuRef, SlashCommandMenuProps>(
  (props, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0)

    useEffect(() => {
      setSelectedIndex(0)
    }, [props.items])

    const selectItem = (index: number) => {
      const item = props.items[index]
      if (item) {
        props.command(item)
      }
    }

    const upHandler = () => {
      setSelectedIndex((selectedIndex + props.items.length - 1) % props.items.length)
    }

    const downHandler = () => {
      setSelectedIndex((selectedIndex + 1) % props.items.length)
    }

    const enterHandler = () => {
      selectItem(selectedIndex)
    }

    useImperativeHandle(ref, () => ({
      onKeyDown: ({ event }: { event: KeyboardEvent }) => {
        if (event.key === 'ArrowUp') {
          upHandler()
          return true
        }

        if (event.key === 'ArrowDown') {
          downHandler()
          return true
        }

        if (event.key === 'Enter') {
          enterHandler()
          return true
        }

        return false
      }
    }))

    return (
      <div className="slash-command-menu">
        {props.items.length > 0 ? (
          props.items.map((item, index) => (
            <button
              className={`slash-command-item ${index === selectedIndex ? 'selected' : ''}`}
              key={index}
              onClick={() => selectItem(index)}
              type="button"
            >
              <div className="slash-command-icon">{item.icon}</div>
              <div className="slash-command-content">
                <div className="slash-command-title">{item.title}</div>
                <div className="slash-command-description">{item.description}</div>
              </div>
            </button>
          ))
        ) : (
          <div className="slash-command-empty">No results</div>
        )}
      </div>
    )
  }
)

SlashCommandMenu.displayName = 'SlashCommandMenu'
