import { useEffect, useState } from 'react'
import { fetchLocations, fetchGameSystems } from '../api'
import SubscribeForm from './SubscribeForm'

export default function SubscribeModal({ onClose }) {
  const [locations, setLocations] = useState([])
  const [gameSystems, setGameSystems] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([fetchLocations(), fetchGameSystems()])
      .then(([l, gs]) => {
        setLocations(l)
        setGameSystems(gs)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div
      className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 text-xl leading-none font-bold"
          aria-label="Close"
        >
          ×
        </button>
        <div className="p-6">
          {loading ? (
            <div className="py-8 text-center text-sm text-gray-400">Loading…</div>
          ) : (
            <SubscribeForm locations={locations} gameSystems={gameSystems} />
          )}
        </div>
      </div>
    </div>
  )
}
