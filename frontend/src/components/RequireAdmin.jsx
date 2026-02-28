import { useAuth0 } from '@auth0/auth0-react'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useIsAdmin from '../hooks/useIsAdmin'
import RequireAuth from './RequireAuth'

/**
 * Inner guard: user is authenticated (guaranteed by RequireAuth wrapper),
 * but we still need to verify admin role.
 */
function AdminGate({ children }) {
  const { isLoading } = useAuth0()
  const isAdmin = useIsAdmin()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && !isAdmin) {
      navigate('/')
    }
  }, [isLoading, isAdmin, navigate])

  if (isLoading || !isAdmin) return null
  return children
}

/**
 * Wraps children requiring the user to be logged in AND have the admin role.
 * Non-admins are redirected to /.
 */
export default function RequireAdmin({ children }) {
  return (
    <RequireAuth>
      <AdminGate>{children}</AdminGate>
    </RequireAuth>
  )
}
