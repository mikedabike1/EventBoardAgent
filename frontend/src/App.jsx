import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import StorePage from './pages/StorePage'
import GameSystemPage from './pages/GameSystemPage'

function Nav() {
  return (
    <header className="bg-purple-700 text-white shadow-md">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-6">
        <Link to="/" className="text-xl font-bold tracking-tight hover:text-purple-200 transition-colors">
          🎲 Wargame Event Finder
        </Link>
      </div>
    </header>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Nav />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/stores/:storeId" element={<StorePage />} />
            <Route path="/games/:gameSystemId" element={<GameSystemPage />} />
          </Routes>
        </main>
        <footer className="bg-gray-800 text-gray-400 text-center py-4 text-sm">
          © {new Date().getFullYear()} Wargame Event Finder — Find your next battle
        </footer>
      </div>
    </BrowserRouter>
  )
}
