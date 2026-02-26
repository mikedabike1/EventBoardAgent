import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom'
import Home from './pages/Home'
import LocationPage from './pages/LocationPage'
import GameSystemPage from './pages/GameSystemPage'
import SubscribeModal from './components/SubscribeModal'

// Wrapper components supply a key based on the route param so that the detail
// page fully remounts (fresh loading state) whenever the id changes.
function LocationRoute() {
  const { locationId } = useParams()
  return <LocationPage key={locationId} />
}

function GameSystemRoute() {
  const { gameSystemId } = useParams()
  return <GameSystemPage key={gameSystemId} />
}

function Nav({ onSubscribeClick }) {
  return (
    <header className="bg-purple-700 text-white shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-6">
        <Link to="/" className="text-xl font-bold tracking-tight hover:text-purple-200 transition-colors">
          🎲 Wargame Event Finder
        </Link>
        <button
          onClick={onSubscribeClick}
          className="text-sm px-4 py-1.5 rounded-lg bg-white text-purple-700 font-semibold hover:bg-purple-50 transition-colors"
        >
          ✉ Get Email Updates
        </button>
      </div>
    </header>
  )
}

export default function App() {
  const [showSubscribeModal, setShowSubscribeModal] = useState(false)

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Nav onSubscribeClick={() => setShowSubscribeModal(true)} />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/locations/:locationId" element={<LocationRoute />} />
            <Route path="/games/:gameSystemId" element={<GameSystemRoute />} />
          </Routes>
        </main>
        <footer className="bg-gray-800 text-gray-400 text-center py-4 text-sm">
          © {new Date().getFullYear()} Wargame Event Finder — Find your next battle
        </footer>
      </div>

      {showSubscribeModal && (
        <SubscribeModal onClose={() => setShowSubscribeModal(false)} />
      )}
    </BrowserRouter>
  )
}
