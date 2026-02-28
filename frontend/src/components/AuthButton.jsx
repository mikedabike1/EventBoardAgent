import { useAuth0 } from '@auth0/auth0-react'
import { useState } from 'react'

export default function AuthButton() {
  const { isAuthenticated, isLoading, user, loginWithRedirect, logout } = useAuth0()
  const [menuOpen, setMenuOpen] = useState(false)

  if (isLoading) {
    return (
      <div className="text-sm px-4 py-1.5 text-purple-200 animate-pulse">Loading…</div>
    )
  }

  if (!isAuthenticated) {
    return (
      <button
        onClick={() => loginWithRedirect()}
        className="text-sm px-4 py-1.5 rounded-lg bg-white text-purple-700 font-semibold hover:bg-purple-50 transition-colors"
      >
        Login
      </button>
    )
  }

  return (
    <div className="relative">
      <button
        onClick={() => setMenuOpen((o) => !o)}
        className="flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg bg-white/20 hover:bg-white/30 transition-colors text-white"
      >
        {user.picture && (
          <img
            src={user.picture}
            alt={user.name}
            className="w-6 h-6 rounded-full"
          />
        )}
        <span className="max-w-[120px] truncate">{user.name ?? user.email}</span>
        <span className="text-xs">▾</span>
      </button>

      {menuOpen && (
        <div
          className="absolute right-0 mt-1 w-40 bg-white rounded-lg shadow-lg py-1 z-50 text-sm text-gray-700"
          onBlur={() => setMenuOpen(false)}
        >
          <button
            onClick={() => {
              setMenuOpen(false)
              logout({ logoutParams: { returnTo: window.location.origin } })
            }}
            className="w-full text-left px-4 py-2 hover:bg-gray-100"
          >
            Logout
          </button>
        </div>
      )}
    </div>
  )
}
