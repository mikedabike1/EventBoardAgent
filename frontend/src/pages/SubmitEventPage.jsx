import { useEffect, useState } from 'react'
import { fetchGameSystems, fetchLocations } from '../api'
import useAuthAxios from '../hooks/useAuthAxios'

export default function SubmitEventPage() {
  const authApi = useAuthAxios()
  const [locations, setLocations] = useState([])
  const [gameSystems, setGameSystems] = useState([])
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState(null)
  const [form, setForm] = useState({
    location_name: '',
    game_system: '',
    title: '',
    date: '',
    time: '',
    description: '',
    source_url: '',
    source_type: 'other',
  })

  useEffect(() => {
    fetchLocations().then(setLocations).catch(console.error)
    fetchGameSystems().then(setGameSystems).catch(console.error)
  }, [])

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      await authApi.post('/events/submit', form)
      setSubmitted(true)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Submission failed. Please try again.')
    }
  }

  if (submitted) {
    return (
      <div className="max-w-lg mx-auto mt-16 p-8 bg-white rounded-xl shadow text-center">
        <div className="text-4xl mb-4">🎲</div>
        <h2 className="text-xl font-bold text-gray-800 mb-2">Event Submitted!</h2>
        <p className="text-gray-500 mb-6">
          Your event has been submitted for admin review and will appear on the board once approved.
        </p>
        <button
          onClick={() => {
            setSubmitted(false)
            setForm({
              location_name: '',
              game_system: '',
              title: '',
              date: '',
              time: '',
              description: '',
              source_url: '',
              source_type: 'other',
            })
          }}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold"
        >
          Submit Another
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto mt-8 px-4">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Submit an Event</h1>
      <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
          <input
            name="location_name"
            value={form.location_name}
            onChange={handleChange}
            required
            list="locations-list"
            placeholder="Store or venue name"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <datalist id="locations-list">
            {locations.map((l) => (
              <option key={l.id} value={l.name} />
            ))}
          </datalist>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Game System *</label>
          <input
            name="game_system"
            value={form.game_system}
            onChange={handleChange}
            required
            list="games-list"
            placeholder="e.g. Warhammer 40,000"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <datalist id="games-list">
            {gameSystems.map((g) => (
              <option key={g.id} value={g.name} />
            ))}
          </datalist>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Event Title *</label>
          <input
            name="title"
            value={form.title}
            onChange={handleChange}
            required
            placeholder="e.g. Friday Night 40K"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date *</label>
            <input
              name="date"
              type="date"
              value={form.date}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
            <input
              name="time"
              type="time"
              value={form.time}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            rows={3}
            placeholder="Optional details about the event"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Source URL</label>
          <input
            name="source_url"
            type="url"
            value={form.source_url}
            onChange={handleChange}
            placeholder="https://facebook.com/events/..."
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
          <select
            name="source_type"
            value={form.source_type}
            onChange={handleChange}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="facebook">Facebook</option>
            <option value="discord">Discord</option>
            <option value="website">Website</option>
            <option value="other">Other</option>
          </select>
        </div>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
        )}

        <button
          type="submit"
          className="w-full py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold"
        >
          Submit Event
        </button>
      </form>
    </div>
  )
}
