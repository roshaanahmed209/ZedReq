/**
 * Returns true when a media URL should not be loaded in <img> / <video> (known placeholders, invalid).
 * Seed scripts historically used https://example.com/media/*.jpg which always 404s.
 */
export function shouldSkipMediaLoad(url) {
  if (url == null || typeof url !== 'string') return true
  const s = url.trim()
  if (!s) return true
  const lower = s.toLowerCase()
  if (lower.startsWith('data:image/') || lower.startsWith('data:video/') || lower.startsWith('data:audio/')) {
    return false
  }
  if (lower.startsWith('/') && !lower.startsWith('//')) return false
  try {
    const base = typeof window !== 'undefined' && window.location?.origin ? window.location.origin : 'https://local.invalid'
    const u = new URL(s, base)
    const host = u.hostname.toLowerCase()
    if (host === 'example.com' || host === 'www.example.com' || host.endsWith('.example.com')) return true
    if (host === 'example.org' || host === 'www.example.org' || host.endsWith('.example.org')) return true
    if (host === 'example.net' || host.endsWith('.example.net')) return true
    return false
  } catch {
    return true
  }
}
