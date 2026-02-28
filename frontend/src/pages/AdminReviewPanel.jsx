import { useCallback, useEffect, useState } from 'react'
import useAuthAxios from '../hooks/useAuthAxios'

export default function AdminReviewPanel() {
  const authApi = useAuthAxios()
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadQueue = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await authApi.get('/admin/review').then((r) => r.data)
      setEvents(data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to load review queue.')
    } finally {
      setLoading(false)
    }
  }, [authApi])

  useEffect(() => {
    loadQueue()
  }, [loadQueue])

  async function handleReview(id, action) {
    try {
      await authApi.patch(`/admin/events/${id}/review`, { action })
      setEvents((prev) => prev.filter((e) => e.id !== id))
    } catch (err) {
      alert(err.response?.data?.detail ?? `Failed to ${action} event.`)
    }
  }

  return (
    <div className="max-w-5xl mx-auto mt-8 px-4">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Admin Review Queue</h1>

      {loading && <p className="text-gray-500">Loading…</p>}
      {error && <p className="text-red-600 bg-red-50 rounded-lg px-4 py-2">{error}</p>}

      {!loading && events.length === 0 && !error && (
        <div className="bg-white rounded-xl shadow p-8 text-center text-gray-500">
          No events pending review.
        </div>
      )}

      {events.length > 0 && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Title</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Location</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Game System</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Date</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Submitted By</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {event.source_url ? (
                      <a
                        href={event.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:text-purple-600 underline underline-offset-2"
                      >
                        {event.title}
                      </a>
                    ) : (
                      event.title
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{event.location?.name}</td>
                  <td className="px-4 py-3 text-gray-600">{event.game_system?.name}</td>
                  <td className="px-4 py-3 text-gray-600">{event.date}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs truncate max-w-[160px]">
                    {event.submitted_by ?? '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleReview(event.id, 'approve')}
                        className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-xs font-semibold"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleReview(event.id, 'reject')}
                        className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 transition-colors text-xs font-semibold"
                      >
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
