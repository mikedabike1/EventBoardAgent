import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchEvents, fetchLocations } from '../api'
import EventList from '../components/EventList'

export default function LocationPage() {
  const { locationId } = useParams()
  const id = Number(locationId)

  const [location, setLocation] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      fetchLocations(),
      fetchEvents({ locationId: id }),
    ])
      .then(([locations, evts]) => {
        setLocation(locations.find((l) => l.id === id) || null)
        setEvents(evts)
      })
      .catch((err) => setError(err.message || 'Could not load data.'))
      .finally(() => setLoading(false))
  }, [id])

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <Link to="/" className="text-sm text-purple-600 hover:text-purple-800 font-medium">
        ← Back to all events
      </Link>

      {location ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h1 className="text-2xl font-bold text-gray-900">🏪 {location.name}</h1>
          <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
            {location.city && location.state && (
              <span>📍 {location.city}, {location.state}</span>
            )}
            {location.website && (
              <a
                href={location.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-600 hover:text-purple-800"
              >
                🌐 Website
              </a>
            )}
            {location.discord_url && (
              <a
                href={location.discord_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-indigo-600 hover:text-indigo-800"
              >
                💬 Discord
              </a>
            )}
            {location.facebook_url && (
              <a
                href={location.facebook_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                📘 Facebook
              </a>
            )}
          </div>
        </div>
      ) : (
        !loading && (
          <h1 className="text-2xl font-bold text-gray-900">Location #{locationId}</h1>
        )
      )}

      <h2 className="text-lg font-semibold text-gray-700">Upcoming Events</h2>
      <EventList events={events} loading={loading} error={error} />
    </div>
  )
}
