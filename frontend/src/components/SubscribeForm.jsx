import { useState } from 'react'
import { subscribe } from '../api'

export default function SubscribeForm({ stores, gameSystems }) {
  const [email, setEmail] = useState('')
  const [selectedStores, setSelectedStores] = useState([])
  const [selectedGames, setSelectedGames] = useState([])
  const [status, setStatus] = useState(null) // null | 'loading' | 'success' | 'error'
  const [errorMsg, setErrorMsg] = useState('')

  function toggleId(list, setList, id) {
    setList((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id])
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!email) return
    setStatus('loading')
    setErrorMsg('')
    try {
      await subscribe(email, selectedStores, selectedGames)
      setStatus('success')
      setEmail('')
      setSelectedStores([])
      setSelectedGames([])
    } catch (err) {
      setStatus('error')
      setErrorMsg(err?.response?.data?.detail || 'Something went wrong. Please try again.')
    }
  }

  if (status === 'success') {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
        <div className="text-3xl mb-2">✅</div>
        <p className="font-semibold text-green-800">You're subscribed!</p>
        <p className="text-sm text-green-600 mt-1">
          You'll receive a monthly email with events matching your selections.
        </p>
        <button
          className="mt-4 text-sm text-green-700 underline"
          onClick={() => setStatus(null)}
        >
          Subscribe another email
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-bold text-gray-800 mb-1">📬 Get Monthly Event Emails</h2>
      <p className="text-sm text-gray-500 mb-5">
        Choose which stores and game systems you care about. We'll send you a calendar every month.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email address</label>
          <input
            type="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
        </div>

        {stores.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Stores (optional)</p>
            <div className="flex flex-wrap gap-2">
              {stores.map((s) => {
                const checked = selectedStores.includes(s.id)
                return (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => toggleId(selectedStores, setSelectedStores, s.id)}
                    className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                      checked
                        ? 'bg-purple-600 text-white border-purple-600'
                        : 'border-gray-200 text-gray-600 hover:border-purple-400'
                    }`}
                  >
                    {s.name}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {gameSystems.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Game Systems (optional)</p>
            <div className="flex flex-wrap gap-2">
              {gameSystems.map((gs) => {
                const checked = selectedGames.includes(gs.id)
                return (
                  <button
                    key={gs.id}
                    type="button"
                    onClick={() => toggleId(selectedGames, setSelectedGames, gs.id)}
                    className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                      checked
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'border-gray-200 text-gray-600 hover:border-indigo-400'
                    }`}
                  >
                    {gs.name}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {status === 'error' && (
          <p className="text-sm text-red-600">{errorMsg}</p>
        )}

        <button
          type="submit"
          disabled={status === 'loading'}
          className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg transition-colors text-sm"
        >
          {status === 'loading' ? 'Subscribing…' : 'Subscribe'}
        </button>
      </form>
    </div>
  )
}
