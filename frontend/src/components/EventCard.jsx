import { Link } from 'react-router-dom'

const SOURCE_ICONS = {
  facebook: '📘',
  discord: '💬',
  website: '🌐',
}

const SOURCE_LABELS = {
  facebook: 'Facebook',
  discord: 'Discord',
  website: 'Website',
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })
}

export default function EventCard({ event }) {
  const icon = SOURCE_ICONS[event.source_type] || '📅'
  const label = SOURCE_LABELS[event.source_type] || event.source_type

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 text-base leading-snug mb-1 truncate">
            {event.title}
          </h3>

          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 mb-3">
            <span className="flex items-center gap-1">
              📅 {formatDate(event.date)}{event.start_time ? ` at ${event.start_time}` : ''}
            </span>
            <Link
              to={`/stores/${event.store.id}`}
              className="flex items-center gap-1 text-purple-600 hover:text-purple-800 font-medium"
            >
              🏪 {event.store.name}
            </Link>
            <Link
              to={`/games/${event.game_system.id}`}
              className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium"
            >
              🎲 {event.game_system.name}
            </Link>
          </div>

          {event.description && (
            <p className="text-sm text-gray-600 line-clamp-2">{event.description}</p>
          )}
        </div>

        {event.source_url && (
          <a
            href={event.source_url}
            target="_blank"
            rel="noopener noreferrer"
            title={`View on ${label}`}
            className="flex-shrink-0 text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
          >
            {icon} {label}
          </a>
        )}
      </div>
    </div>
  )
}
