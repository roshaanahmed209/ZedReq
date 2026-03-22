/**
 * Normalize API error payloads from the backend.
 * Custom StarletteHTTPException handler returns { success, message, status_code }.
 * Standard FastAPI validation uses { detail: string | ValidationError[] }.
 */
export function extractApiErrorMessage(data) {
  if (data == null) return null

  if (typeof data.message === 'string' && data.message.trim()) {
    return data.message.trim()
  }

  const detail = data.detail
  if (detail == null) return null
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((x) => (typeof x === 'object' && x?.msg ? x.msg : String(x)))
      .join(' ')
  }
  if (typeof detail === 'object' && detail?.msg) return String(detail.msg)
  return String(detail)
}
