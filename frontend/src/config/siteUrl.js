/**
 * Canonical public site origin (no trailing slash).
 * Set ZEDREQ_URL or VITE_ZEDREQ_URL in the repo root .env; Vite maps it to import.meta.env.VITE_ZEDREQ_URL.
 */
export function getSiteBaseUrl() {
  const raw = import.meta.env.VITE_ZEDREQ_URL
  if (raw == null || String(raw).trim() === '') {
    return ''
  }
  return String(raw).replace(/\/$/, '')
}

/** Absolute URL for a path (e.g. /privacy). Falls back to a root-relative path if base is unset. */
export function sitePath(pathname) {
  const base = getSiteBaseUrl()
  const path = pathname.startsWith('/') ? pathname : `/${pathname}`
  if (!base) return path
  return `${base}${path}`
}
