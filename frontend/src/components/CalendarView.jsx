import { useState } from 'react'
import { Link } from 'react-router-dom'

const DAY_HEADERS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Stable color per game-system id so the same game always gets the same pill color
const PILL_COLORS = [
  'bg-purple-100 text-purple-800',
  'bg-indigo-100 text-indigo-800',
  'bg-sky-100 text-sky-800',
  'bg-emerald-100 text-emerald-800',
  'bg-amber-100 text-amber-800',
  'bg-rose-100 text-rose-800',
  'bg-teal-100 text-teal-800',
]

function pillColor(gameSystemId) {
  return PILL_COLORS[(gameSystemId - 1) % PILL_COLORS.length]
}

function toDateStr(year, month, day) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

function monthLabel(year, month) {
  return new Date(year, month, 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}

function formatTime(t) {
  if (!t) return ''
  const [h, m] = t.split(':').map(Number)
  const ampm = h >= 12 ? 'pm' : 'am'
  const h12 = h % 12 || 12
  return `${h12}:${String(m).padStart(2, '0')} ${ampm}`
}

// ── Day detail panel ─────────────────────────────────────────────────────────

function DayPanel({ dateStr, events, onClose }) {
  const d = new Date(dateStr + 'T00:00:00')
  const label = d.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })

  return (
    <div className="mt-4 bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100 bg-gray-50">
        <p className="font-semibold text-gray-800 text-sm">{label}</p>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-lg leading-none">✕</button>
      </div>
      <div className="divide-y divide-gray-50">
        {events.map((e) => (
          <div key={e.id} className="px-5 py-3 flex items-start gap-3">
            <span className={`mt-0.5 shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${pillColor(e.game_system.id)}`}>
              {e.game_system.name}
            </span>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-gray-900 text-sm">{e.title}</p>
              <div className="flex flex-wrap gap-x-3 text-xs text-gray-500 mt-0.5">
                {e.start_time && <span>{formatTime(e.start_time)}</span>}
                <Link to={`/locations/${e.location.id}`} className="text-purple-600 hover:underline">
                  {e.location.name}
                </Link>
              </div>
              {e.description && (
                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{e.description}</p>
              )}
            </div>
            {e.source_url && (
              <a
                href={e.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="shrink-0 text-xs text-gray-400 hover:text-gray-600"
              >
                ↗
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Main calendar ─────────────────────────────────────────────────────────────

export default function CalendarView({ events }) {
  const todayDate = new Date()
  const todayStr = todayDate.toISOString().split('T')[0]

  // Default to the month of the first event, otherwise use today's month
  const initMonth = () => {
    if (events.length > 0) {
      const d = new Date(events[0].date + 'T00:00:00')
      return { year: d.getFullYear(), month: d.getMonth() }
    }
    return { year: todayDate.getFullYear(), month: todayDate.getMonth() }
  }
  const init = initMonth()
  const [viewYear, setViewYear] = useState(init.year)
  const [viewMonth, setViewMonth] = useState(init.month)
  const [selectedDate, setSelectedDate] = useState(null)

  // Group events by 'YYYY-MM-DD'
  const eventsByDate = {}
  for (const e of events) {
    if (!eventsByDate[e.date]) eventsByDate[e.date] = []
    eventsByDate[e.date].push(e)
  }

  // Build grid: leading blank cells + days 1..N
  const firstDow = new Date(viewYear, viewMonth, 1).getDay()
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate()
  const cells = [
    ...Array(firstDow).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]
  // Pad to complete the last row (for visual consistency)
  while (cells.length % 7 !== 0) cells.push(null)

  function prevMonth() {
    if (viewMonth === 0) { setViewYear((y) => y - 1); setViewMonth(11) }
    else setViewMonth((m) => m - 1)
    setSelectedDate(null)
  }

  function nextMonth() {
    if (viewMonth === 11) { setViewYear((y) => y + 1); setViewMonth(0) }
    else setViewMonth((m) => m + 1)
    setSelectedDate(null)
  }

  function handleDayClick(dateStr, hasEvents) {
    if (!hasEvents) return
    setSelectedDate((prev) => (prev === dateStr ? null : dateStr))
  }

  const selectedEvents = selectedDate ? (eventsByDate[selectedDate] || []) : []

  return (
    <div>
      {/* Month navigation */}
      <div className="flex items-center justify-between mb-3">
        <button
          onClick={prevMonth}
          className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-gray-600"
        >
          ← Prev
        </button>
        <h2 className="font-semibold text-gray-800 text-base">{monthLabel(viewYear, viewMonth)}</h2>
        <button
          onClick={nextMonth}
          className="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors text-gray-600"
        >
          Next →
        </button>
      </div>

      {/* Grid */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        {/* Day-of-week headers */}
        <div className="grid grid-cols-7 border-b border-gray-100">
          {DAY_HEADERS.map((d) => (
            <div key={d} className="py-2 text-center text-xs font-semibold text-gray-400 uppercase tracking-wide">
              {d}
            </div>
          ))}
        </div>

        {/* Day cells */}
        <div className="grid grid-cols-7">
          {cells.map((day, idx) => {
            if (!day) {
              return <div key={`blank-${idx}`} className="min-h-24 bg-gray-50/50 border-r border-b border-gray-50" />
            }

            const dateStr = toDateStr(viewYear, viewMonth, day)
            const dayEvents = eventsByDate[dateStr] || []
            const hasEvents = dayEvents.length > 0
            const isToday = dateStr === todayStr
            const isSelected = dateStr === selectedDate
            const overflow = dayEvents.length > 3 ? dayEvents.length - 3 : 0

            return (
              <div
                key={dateStr}
                onClick={() => handleDayClick(dateStr, hasEvents)}
                className={[
                  'min-h-24 p-1.5 border-r border-b border-gray-50 flex flex-col transition-colors',
                  hasEvents ? 'cursor-pointer' : '',
                  isSelected ? 'bg-purple-50' : hasEvents ? 'hover:bg-gray-50' : '',
                ].join(' ')}
              >
                {/* Day number */}
                <div className="flex justify-end mb-1">
                  <span className={[
                    'text-xs font-semibold w-6 h-6 flex items-center justify-center rounded-full',
                    isToday
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-600',
                  ].join(' ')}>
                    {day}
                  </span>
                </div>

                {/* Event pills */}
                <div className="flex flex-col gap-0.5 flex-1">
                  {dayEvents.slice(0, 3).map((e) => (
                    <div
                      key={e.id}
                      className={`text-xs px-1.5 py-0.5 rounded font-medium truncate ${pillColor(e.game_system.id)}`}
                      title={`${e.title} — ${e.game_system.name}`}
                    >
                      {e.title}
                    </div>
                  ))}
                  {overflow > 0 && (
                    <div className="text-xs text-gray-400 pl-1">+{overflow} more</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Selected day detail panel */}
      {selectedDate && selectedEvents.length > 0 && (
        <DayPanel
          dateStr={selectedDate}
          events={selectedEvents}
          onClose={() => setSelectedDate(null)}
        />
      )}

      {/* Legend */}
      {events.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {[...new Map(events.map((e) => [e.game_system.id, e.game_system])).values()].map((gs) => (
            <span key={gs.id} className={`text-xs px-2 py-0.5 rounded-full font-medium ${pillColor(gs.id)}`}>
              {gs.name}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
