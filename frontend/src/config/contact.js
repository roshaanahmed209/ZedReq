/**
 * Primary ZedReq contact email (support, privacy, careers inquiries, legal footers).
 * Set ZEDREQ_EMAIL or VITE_ZEDREQ_EMAIL in the repo root .env; Vite exposes it as import.meta.env.VITE_ZEDREQ_EMAIL.
 */
const DEFAULT_EMAIL = 'zed.req@yahoo.com'

export const ZEDREQ_EMAIL =
  (import.meta.env.VITE_ZEDREQ_EMAIL && String(import.meta.env.VITE_ZEDREQ_EMAIL).trim()) ||
  DEFAULT_EMAIL

/** mailto: URL; optional subject for pre-filled subject line */
export function zedreqMailto(subject) {
  if (subject == null || subject === '') {
    return `mailto:${ZEDREQ_EMAIL}`
  }
  return `mailto:${ZEDREQ_EMAIL}?subject=${encodeURIComponent(subject)}`
}
