import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchEvents, fetchGameSystems } from '../api'
import EventList from '../components/EventList'

export default function GameSystemPage() {
  const { gameSystemId } = useParams()
  const id = Number(gameSystemId)

  const [gameSystem, setGameSystem] = useState(null)
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([
      fetchGameSystems(),
      fetchEvents({ gameSystemId: id }),
    ])
      .then(([gameSystems, evts]) => {
        setGameSystem(gameSystems.find((gs) => gs.id === id) || null)
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

      {gameSystem ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h1 className="text-2xl font-bold text-gray-900">🎲 {gameSystem.name}</h1>
          {gameSystem.publisher && (
            <p className="text-sm text-gray-500 mt-1">Published by {gameSystem.publisher}</p>
          )}
        </div>
      ) : (
        !loading && (
          <h1 className="text-2xl font-bold text-gray-900">Game System #{gameSystemId}</h1>
        )
      )}

      <h2 className="text-lg font-semibold text-gray-700">Upcoming Events</h2>
      <EventList events={events} loading={loading} error={error} />
    </div>
  )
}
