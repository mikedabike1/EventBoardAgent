import { Link } from 'react-router-dom'

const SOURCE_ICONS = {
  facebook: '📘',
  discord: '💬',
  website: '🌐',
  eventbrite: '🎟️',
}

const SOURCE_LABELS = {
  facebook: 'Facebook',
  discord: 'Discord',
  website: 'Website',
  eventbrite: 'Eventbrite',
}

const SOURCE_COLORS = {
  facebook: 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100',
  discord: 'bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100',
  website: 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100',
  eventbrite: 'bg-orange-50 border-orange-200 text-orange-700 hover:bg-orange-100',
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
}

export default function EventCard({ event }) {
  const icon = SOURCE_ICONS[event.source_type] || '📅'
  const label = SOURCE_LABELS[event.source_type] || event.source_type
  const colors = SOURCE_COLORS[event.source_type] || 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900 text-base leading-snug mb-1 truncate">
          {event.title}
        </h3>

        <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 mb-3">
          <span className="flex items-center gap-1">
            📅 {formatDate(event.date)}{event.start_time ? ` at ${event.start_time}` : ''}
          </span>
          <Link
            to={`/locations/${event.location.id}`}
            className="flex items-center gap-1 text-purple-600 hover:text-purple-800 font-medium"
          >
            🏪 {event.location.name}
          </Link>
          <Link
            to={`/games/${event.game_system.id}`}
            className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium"
          >
            🎲 {event.game_system.name}
          </Link>
        </div>

        {event.description && (
          <p className="text-sm text-gray-600 line-clamp-2 mb-3">{event.description}</p>
        )}

        {event.source_url && (
          <a
            href={event.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${colors}`}
          >
            {icon} View on {label} ↗
          </a>
        )}
      </div>
    </div>
  )
}
