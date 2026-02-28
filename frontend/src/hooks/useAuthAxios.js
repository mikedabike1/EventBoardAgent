import { useAuth0 } from '@auth0/auth0-react'
import axios from 'axios'
import { useMemo } from 'react'

/**
 * Returns an axios instance that automatically injects a fresh Auth0 access
 * token as the Authorization header on every request.
 *
 * Usage:
 *   const authApi = useAuthAxios()
 *   const data = await authApi.get('/admin/review').then(r => r.data)
 */
export default function useAuthAxios() {
  const { getAccessTokenSilently } = useAuth0()

  const instance = useMemo(() => {
    const api = axios.create({
      baseURL: import.meta.env.VITE_API_URL ?? '',
      headers: { 'Content-Type': 'application/json' },
    })

    api.interceptors.request.use(async (config) => {
      const token = await getAccessTokenSilently()
      config.headers.Authorization = `Bearer ${token}`
      return config
    })

    return api
  }, [getAccessTokenSilently])

  return instance
}
