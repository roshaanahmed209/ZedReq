/**
 * Analytics identity primitives: the anonymous visitor id and the session id.
 *
 * These live in their own module because both `utils/analytics.js` (which sends the
 * events) and `services/api.js` (which attaches the anonymous id to auth requests so
 * the server can stitch the visitor to their new account) need them. Importing one
 * from the other would create a cycle.
 *
 * Every storage access is guarded: private browsing, disabled storage and sandboxed
 * iframes all make localStorage throw, and none of that is a reason for the app to
 * break. When storage is unavailable, tracking quietly degrades.
 */

const ANON_ID_KEY = 'zq_anon_id'
const SESSION_ID_KEY = 'zq_session_id'
const SESSION_LAST_SEEN_KEY = 'zq_session_last_seen'

/** Matches SESSION_TIMEOUT_MINUTES in the back office config. */
export const SESSION_TIMEOUT_MS = 30 * 60 * 1000

export function readLocal(key) {
  try {
    return window.localStorage.getItem(key)
  } catch {
    return null
  }
}

export function writeLocal(key, value) {
  try {
    window.localStorage.setItem(key, value)
  } catch {
    /* storage unavailable */
  }
}

export function removeLocal(key) {
  try {
    window.localStorage.removeItem(key)
  } catch {
    /* storage unavailable */
  }
}

export function readJSON(key) {
  const raw = readLocal(key)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function writeJSON(key, value) {
  try {
    writeLocal(key, JSON.stringify(value))
  } catch {
    /* ignore */
  }
}

/** Random, URL-safe id. Falls back progressively when crypto is unavailable. */
export function randomId() {
  try {
    if (window.crypto?.randomUUID) {
      return window.crypto.randomUUID().replace(/-/g, '')
    }
    if (window.crypto?.getRandomValues) {
      const bytes = new Uint8Array(16)
      window.crypto.getRandomValues(bytes)
      return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
    }
  } catch {
    /* fall through */
  }
  return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 12)}`
}

/**
 * Stable per-browser visitor id, persisted in localStorage.
 *
 * Survives across pages, tabs and sessions. This persistence is what makes it
 * possible to join a visitor's pre-signup journey to the account they create later.
 */
export function getAnonymousId() {
  let id = readLocal(ANON_ID_KEY)
  if (!id || id.length < 6) {
    id = randomId()
    writeLocal(ANON_ID_KEY, id)
  }
  return id
}

/**
 * Current session id, rotated after 30 minutes of inactivity.
 *
 * Kept in localStorage rather than sessionStorage on purpose: with sessionStorage a
 * second tab would start a second session and split one visit in two.
 */
export function getSessionId() {
  const now = Date.now()
  const lastSeen = parseInt(readLocal(SESSION_LAST_SEEN_KEY) || '0', 10)
  let sessionId = readLocal(SESSION_ID_KEY)

  if (!sessionId || !lastSeen || now - lastSeen > SESSION_TIMEOUT_MS) {
    sessionId = randomId()
    writeLocal(SESSION_ID_KEY, sessionId)
  }

  writeLocal(SESSION_LAST_SEEN_KEY, String(now))
  return sessionId
}
