export const FEATURE_LABELS = {
  ai_messages: 'AI Messages (Nemz)',
  course_enrollments: 'Course Enrollments (LMS)',
  interview_sessions: 'AI Mock Interviews',
}

export const PLAN_LABELS = {
  free: 'Explorer (Free)',
  pro: 'Professional',
  premium: 'Elite',
  enterprise: 'Enterprise',
}

/**
 * Parse a 403 API error into a structured payload for the access-denied modal.
 */
export function parseAccessDeniedError(err) {
  if (err?.response?.status !== 403) return null

  const detail = err.response?.data?.detail

  if (detail && typeof detail === 'object' && (detail.feature || detail.message)) {
    const limit = detail.limit
    const used = detail.used
    return {
      type: detail.feature ? 'quota' : 'forbidden',
      message:
        detail.message ||
        err.userMessage ||
        'You do not have access to this feature.',
      feature: detail.feature || null,
      used: used ?? null,
      limit: limit ?? null,
      remaining:
        limit != null && used != null && limit !== -1
          ? Math.max(0, limit - used)
          : null,
      plan: detail.plan || null,
    }
  }

  const message =
    (typeof detail === 'string' && detail) ||
    detail?.message ||
    err.userMessage ||
    'Access denied'

  return {
    type: 'forbidden',
    message,
    feature: null,
    used: null,
    limit: null,
    remaining: null,
    plan: null,
  }
}

export function formatPlanName(plan) {
  if (!plan) return null
  return PLAN_LABELS[plan] || `${plan.charAt(0).toUpperCase()}${plan.slice(1)}`
}

export function formatUsageLine(used, limit) {
  if (limit === -1) return `${used ?? 0} / Unlimited`
  return `${used ?? 0} / ${limit ?? 0}`
}

export function usagePercent(used, limit) {
  if (limit == null || limit <= 0 || limit === -1) return 0
  return Math.min(100, Math.round(((used ?? 0) / limit) * 100))
}
