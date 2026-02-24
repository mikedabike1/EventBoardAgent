import axios from 'axios'

const api = axios.create({
  // In dev: Vite's proxy forwards relative requests to localhost:8000.
  // In production (served from FastAPI): relative URLs hit the same host,
  // so the app works on any IP or domain without rebuilding.
  // VITE_API_URL can still override this for external backends.
  baseURL: import.meta.env.VITE_API_URL ?? '',
  headers: { 'Content-Type': 'application/json' },
})

export const fetchEvents = (filters = {}) => {
  const params = {}
  if (filters.locationId != null) params.location_id = filters.locationId
  if (filters.gameSystemId != null) params.game_system_id = filters.gameSystemId
  if (filters.dateFrom) params.date_from = filters.dateFrom
  if (filters.dateTo) params.date_to = filters.dateTo
  if (filters.skip != null) params.skip = filters.skip
  if (filters.limit != null) params.limit = filters.limit
  return api.get('/events', { params }).then((r) => r.data)
}

export const fetchLocations = () => api.get('/locations').then((r) => r.data)

export const fetchGameSystems = () => api.get('/games').then((r) => r.data)

export const subscribe = (email, locationIds, gameSystemIds) =>
  api
    .post('/subscribe', { email, location_ids: locationIds, game_system_ids: gameSystemIds })
    .then((r) => r.data)

export default api
