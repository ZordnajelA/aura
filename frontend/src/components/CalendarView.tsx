import React, { useState, useEffect } from 'react'

interface CalendarViewProps {
  selectedDate: Date
  datesWithNotes: Set<string>
  onDateSelect: (date: Date) => void
}

const CalendarView: React.FC<CalendarViewProps> = ({
  selectedDate,
  datesWithNotes,
  onDateSelect,
}) => {
  const [currentMonth, setCurrentMonth] = useState(new Date(selectedDate))

  useEffect(() => {
    setCurrentMonth(new Date(selectedDate))
  }, [selectedDate])

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    return new Date(year, month + 1, 0).getDate()
  }

  const getFirstDayOfMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    return new Date(year, month, 1).getDay()
  }

  const formatDateKey = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  const isToday = (date: Date): boolean => {
    const today = new Date()
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const isSameDay = (date1: Date, date2: Date): boolean => {
    return (
      date1.getDate() === date2.getDate() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getFullYear() === date2.getFullYear()
    )
  }

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1))
  }

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1))
  }

  const goToToday = () => {
    const today = new Date()
    setCurrentMonth(today)
    onDateSelect(today)
  }

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(currentMonth)
    const firstDay = getFirstDayOfMonth(currentMonth)
    const days = []

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="calendar-day empty" />)
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
      const dateKey = formatDateKey(date)
      const hasNote = datesWithNotes.has(dateKey)
      const today = isToday(date)
      const selected = isSameDay(date, selectedDate)

      days.push(
        <div
          key={day}
          className={`calendar-day ${hasNote ? 'has-note' : ''} ${today ? 'today' : ''} ${
            selected ? 'selected' : ''
          }`}
          onClick={() => onDateSelect(date)}
        >
          <span className="day-number">{day}</span>
          {hasNote && <span className="note-indicator">•</span>}
        </div>
      )
    }

    return days
  }

  return (
    <div className="calendar-view">
      <div className="calendar-header">
        <button onClick={previousMonth} className="nav-button">
          ←
        </button>
        <div className="month-year">
          <span className="month">{monthNames[currentMonth.getMonth()]}</span>
          <span className="year">{currentMonth.getFullYear()}</span>
        </div>
        <button onClick={nextMonth} className="nav-button">
          →
        </button>
      </div>
      <button onClick={goToToday} className="today-button">
        Today
      </button>
      <div className="calendar-weekdays">
        <div className="weekday">Sun</div>
        <div className="weekday">Mon</div>
        <div className="weekday">Tue</div>
        <div className="weekday">Wed</div>
        <div className="weekday">Thu</div>
        <div className="weekday">Fri</div>
        <div className="weekday">Sat</div>
      </div>
      <div className="calendar-grid">{renderCalendar()}</div>

      <style>{`
        .calendar-view {
          background: white;
          border-radius: 8px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .calendar-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .nav-button {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          padding: 0.5rem;
          color: #4f46e5;
          transition: color 0.2s;
        }

        .nav-button:hover {
          color: #4338ca;
        }

        .month-year {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .month {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1f2937;
        }

        .year {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .today-button {
          width: 100%;
          padding: 0.5rem;
          margin-bottom: 1rem;
          background: #4f46e5;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.2s;
        }

        .today-button:hover {
          background: #4338ca;
        }

        .calendar-weekdays {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .weekday {
          text-align: center;
          font-size: 0.75rem;
          font-weight: 600;
          color: #6b7280;
          padding: 0.5rem;
        }

        .calendar-grid {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 0.5rem;
        }

        .calendar-day {
          aspect-ratio: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          cursor: pointer;
          position: relative;
          transition: all 0.2s;
          background: #f9fafb;
        }

        .calendar-day:not(.empty):hover {
          background: #e5e7eb;
        }

        .calendar-day.empty {
          cursor: default;
          background: transparent;
        }

        .calendar-day.today {
          background: #eef2ff;
          border: 2px solid #4f46e5;
        }

        .calendar-day.selected {
          background: #4f46e5;
          color: white;
        }

        .calendar-day.selected .day-number {
          color: white;
        }

        .calendar-day.has-note {
          font-weight: 600;
        }

        .day-number {
          font-size: 0.875rem;
          color: #1f2937;
        }

        .note-indicator {
          position: absolute;
          bottom: 2px;
          font-size: 1.5rem;
          color: #4f46e5;
          line-height: 0;
        }

        .calendar-day.selected .note-indicator {
          color: white;
        }
      `}</style>
    </div>
  )
}

export default CalendarView
