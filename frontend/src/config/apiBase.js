/**
 * Base URL for API and WebSocket calls.
 *
 * Set VITE_API_URL when the API is on another host (local backend, Render).
 * Leave it unset on Vercel: the browser calls this same origin, and vercel.json
 * sends /api and /ws to the backend service. A service binding cannot supply
 * this value — bindings exist only inside server functions at runtime, and
 * these requests run in the browser.
 */
export function getApiBaseUrl() {
  const configured = String(import.meta.env.VITE_API_URL ?? '').trim().replace(/\/$/, '')
  if (configured) return configured
  return import.meta.env.DEV ? 'http://localhost:5000' : ''
}

export function getWebSocketBaseUrl() {
  const apiUrl = getApiBaseUrl()
  if (apiUrl) {
    return apiUrl.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}`
}
