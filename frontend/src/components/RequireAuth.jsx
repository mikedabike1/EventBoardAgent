import { useAuth0 } from '@auth0/auth0-react'
import { useEffect } from 'react'

/**
 * Wraps children requiring the user to be logged in.
 * Redirects to Auth0 login if not authenticated.
 */
export default function RequireAuth({ children }) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      loginWithRedirect({ appState: { returnTo: window.location.pathname } })
    }
  }, [isLoading, isAuthenticated, loginWithRedirect])

  if (isLoading || !isAuthenticated) return null
  return children
}
