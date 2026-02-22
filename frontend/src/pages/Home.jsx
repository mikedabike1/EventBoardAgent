import { useEffect, useState } from 'react'
import { fetchEvents, fetchStores, fetchGameSystems } from '../api'
import FilterBar from '../components/FilterBar'
import EventList from '../components/EventList'
import SubscribeForm from '../components/SubscribeForm'

const today = new Date().toISOString().split('T')[0]

export default function Home() {
  const [stores, setStores] = useState([])
  const [gameSystems, setGameSystems] = useState([])
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    storeId: null,
    gameSystemId: null,
    dateFrom: today,
    dateTo: null,
  })

  // Load stores and game systems once on mount
  useEffect(() => {
    Promise.all([fetchStores(), fetchGameSystems()])
      .then(([s, gs]) => {
        setStores(s)
        setGameSystems(gs)
      })
      .catch(() => {})
  }, [])

  // Load events with current filters
  function loadEvents(activeFilters) {
    setLoading(true)
    setError(null)
    fetchEvents(activeFilters)
      .then(setEvents)
      .catch((err) => setError(err.message || 'Could not load events.'))
      .finally(() => setLoading(false))
  }

  // Load events on first render
  useEffect(() => {
    loadEvents(filters)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSearch() {
    loadEvents(filters)
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Hero */}
      <div className="text-center py-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Find Local Wargame Events</h1>
        <p className="text-gray-500 text-base">
          Discover upcoming miniature wargaming events at stores near you.
        </p>
      </div>

      {/* Filters */}
      <FilterBar
        stores={stores}
        gameSystems={gameSystems}
        filters={filters}
        onChange={setFilters}
        onSearch={handleSearch}
      />

      {/* Results count */}
      {!loading && !error && (
        <p className="text-sm text-gray-500">
          {events.length === 0
            ? 'No events found'
            : `${events.length} event${events.length === 1 ? '' : 's'} found`}
        </p>
      )}

      {/* Event list */}
      <EventList events={events} loading={loading} error={error} />

      {/* Subscribe */}
      {!loading && (
        <div className="pt-6 border-t border-gray-200">
          <SubscribeForm stores={stores} gameSystems={gameSystems} />
        </div>
      )}
    </div>
  )
}
