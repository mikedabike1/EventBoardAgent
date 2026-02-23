import { useEffect, useState } from 'react'
import { fetchEvents, fetchStores, fetchGameSystems } from '../api'
import FilterBar from '../components/FilterBar'
import EventList from '../components/EventList'
import CalendarView from '../components/CalendarView'
import SubscribeForm from '../components/SubscribeForm'

const today = new Date().toISOString().split('T')[0]

export default function Home() {
  const [stores, setStores] = useState([])
  const [gameSystems, setGameSystems] = useState([])
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [view, setView] = useState('list') // 'list' | 'calendar'
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

  // Shared async fetch — all setState calls happen in async callbacks so the
  // lint rule (no synchronous setState in effects) is satisfied when called
  // from the initial useEffect.
  function fetchAndSetEvents(activeFilters) {
    return fetchEvents(activeFilters)
      .then(setEvents)
      .catch((err) => setError(err.message || 'Could not load events.'))
      .finally(() => setLoading(false))
  }

  // Called from user interaction (Search button) — safe to set loading state
  // synchronously here because this is not inside an effect body.
  function handleSearch() {
    setLoading(true)
    setError(null)
    fetchAndSetEvents(filters)
  }

  // Initial load — call only the async helper so no setState runs synchronously
  // inside the effect body.
  useEffect(() => {
    fetchAndSetEvents(filters)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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

      {/* View toggle + results count */}
      {!loading && !error && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            {events.length === 0
              ? 'No events found'
              : `${events.length} event${events.length === 1 ? '' : 's'} found`}
          </p>
          <div className="flex rounded-lg border border-gray-200 overflow-hidden text-sm font-medium">
            <button
              onClick={() => setView('list')}
              className={`px-3 py-1.5 transition-colors ${view === 'list' ? 'bg-purple-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
            >
              ☰ List
            </button>
            <button
              onClick={() => setView('calendar')}
              className={`px-3 py-1.5 border-l border-gray-200 transition-colors ${view === 'calendar' ? 'bg-purple-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
            >
              📅 Calendar
            </button>
          </div>
        </div>
      )}

      {/* Event list or calendar */}
      {view === 'list'
        ? <EventList events={events} loading={loading} error={error} />
        : !loading && <CalendarView events={events} />
      }

      {/* Subscribe */}
      {!loading && (
        <div className="pt-6 border-t border-gray-200">
          <SubscribeForm stores={stores} gameSystems={gameSystems} />
        </div>
      )}
    </div>
  )
}
