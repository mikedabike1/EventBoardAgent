import { useAuth0 } from '@auth0/auth0-react'

const ROLES_CLAIM = 'https://eventboard/roles'

/**
 * Returns true if the current user has the admin role in their Auth0 token.
 */
export default function useIsAdmin() {
  const { user } = useAuth0()
  return Array.isArray(user?.[ROLES_CLAIM]) && user[ROLES_CLAIM].includes('admin')
}
