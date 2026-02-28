import { useAuth0 } from '@auth0/auth0-react'
import { useState } from 'react'
import { BrowserRouter, Link, Route, Routes, useParams } from 'react-router-dom'
import AuthButton from './components/AuthButton'
import RequireAdmin from './components/RequireAdmin'
import RequireAuth from './components/RequireAuth'
import SubscribeModal from './components/SubscribeModal'
import useIsAdmin from './hooks/useIsAdmin'
import AdminReviewPanel from './pages/AdminReviewPanel'
import GameSystemPage from './pages/GameSystemPage'
import Home from './pages/Home'
import LocationPage from './pages/LocationPage'
import SubmitEventPage from './pages/SubmitEventPage'

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
  const { isAuthenticated } = useAuth0()
  const isAdmin = useIsAdmin()

  return (
    <header className="bg-purple-700 text-white shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        <Link to="/" className="text-xl font-bold tracking-tight hover:text-purple-200 transition-colors">
          🎲 Wargame Event Finder
        </Link>
        <div className="flex items-center gap-3">
          {isAuthenticated && (
            <Link
              to="/submit"
              className="text-sm px-4 py-1.5 rounded-lg bg-white/20 hover:bg-white/30 transition-colors text-white font-semibold"
            >
              + Submit Event
            </Link>
          )}
          {isAdmin && (
            <Link
              to="/admin"
              className="text-sm px-4 py-1.5 rounded-lg bg-yellow-400 hover:bg-yellow-300 transition-colors text-yellow-900 font-semibold"
            >
              Admin
            </Link>
          )}
          <button
            onClick={onSubscribeClick}
            className="text-sm px-4 py-1.5 rounded-lg bg-white text-purple-700 font-semibold hover:bg-purple-50 transition-colors"
          >
            ✉ Get Email Updates
          </button>
          <AuthButton />
        </div>
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
            <Route
              path="/submit"
              element={
                <RequireAuth>
                  <SubmitEventPage />
                </RequireAuth>
              }
            />
            <Route
              path="/admin"
              element={
                <RequireAdmin>
                  <AdminReviewPanel />
                </RequireAdmin>
              }
            />
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
