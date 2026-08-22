/**
 * ZedReq first-party analytics SDK.
 *
 * One utility, used everywhere. Call `trackEvent(name, properties)` and the SDK
 * attaches anonymous_id, session_id, timestamp, page context, referrer and UTM
 * information automatically - instrumentation code never has to supply them.
 *
 * Design rules, in priority order:
 *
 *  1. Analytics must never break or slow the product. Every call is wrapped, every
 *     failure is swallowed, nothing is awaited on a user-facing path, and a failed
 *     request is dropped rather than retried forever.
 *  2. Events go to ZedReq's own API, same origin. No third-party script, no secret in
 *     the bundle, nothing for an ad blocker to recognise.
 *  3. Meaningful events only. Page views and sessions are automatic; everything else
 *     is deliberately instrumented. There is no global click listener - auto-tracking
 *     every DOM click produces millions of useless rows and no insight.
 *
 * Events are queued and flushed in batches, and `sendBeacon` is used when the page is
 * being hidden so the last events of a session are not lost on navigation away.
 */

import {
  getAnonymousId,
  getSessionId,
  randomId,
  readJSON,
  readLocal,
  removeLocal,
  writeJSON,
  writeLocal,
} from './analyticsIdentity'

const ENDPOINT = '/api/analytics/events'
const IDENTIFY_ENDPOINT = '/api/analytics/identify'

const FIRST_TOUCH_KEY = 'zq_first_touch'
const LAST_TOUCH_KEY = 'zq_last_touch'
const STITCHED_KEY = 'zq_stitched_user'
const ACCESS_TOKEN_KEY = 'access_token'

const BATCH_SIZE = 10
const FLUSH_INTERVAL_MS = 3000
const MAX_QUEUE = 50

let queue = []
let flushTimer = null
let initialised = false
let lastPath = null

export { getAnonymousId, getSessionId }

// ---------------------------------------------------------------------------
// Attribution
// ---------------------------------------------------------------------------

function readUtmFromUrl() {
  try {
    const params = new URLSearchParams(window.location.search)
    const utm = {}
    for (const key of ['source', 'medium', 'campaign', 'content', 'term']) {
      const value = params.get(`utm_${key}`)
      if (value) utm[`utm_${key}`] = value.slice(0, 160)
    }
    // Ad platforms often send only a click id. Treat that as a paid touch so the
    // visit is not miscounted as organic.
    if (!utm.utm_source) {
      if (params.get('gclid')) utm.utm_source = 'google'
      else if (params.get('fbclid')) utm.utm_source = 'facebook'
      else if (params.get('ttclid')) utm.utm_source = 'tiktok'
      else if (params.get('li_fat_id')) utm.utm_source = 'linkedin'
    }
    return utm
  } catch {
    return {}
  }
}

function externalReferrer() {
  try {
    const ref = document.referrer
    if (!ref) return null
    if (new URL(ref).hostname === window.location.hostname) return null
    return ref.slice(0, 1000)
  } catch {
    return null
  }
}

/**
 * Record acquisition context for this visit.
 *
 * First touch is written exactly once and never overwritten - it is the record of
 * where this person originally discovered ZedReq, and losing it to a later organic
 * visit would make paid-campaign attribution worthless. Last touch is refreshed only
 * when a visit actually carries new acquisition information, so internal navigation
 * cannot overwrite the ad that brought them back.
 */
function captureAttribution() {
  const utm = readUtmFromUrl()
  const referrer = externalReferrer()
  const hasCampaign = Object.keys(utm).length > 0

  if (!hasCampaign && !referrer) return

  const touch = {
    ...utm,
    referrer,
    landing_page: window.location.pathname,
    at: new Date().toISOString(),
  }

  if (!readJSON(FIRST_TOUCH_KEY)) {
    writeJSON(FIRST_TOUCH_KEY, touch)
  }
  writeJSON(LAST_TOUCH_KEY, touch)
}

function currentUtm() {
  // Prefer the UTM on this page load; fall back to the stored last touch so events
  // later in the session stay attributed to the campaign that started it.
  const live = readUtmFromUrl()
  if (Object.keys(live).length > 0) return live

  const stored = readJSON(LAST_TOUCH_KEY) || {}
  const utm = {}
  for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']) {
    if (stored[key]) utm[key] = stored[key]
  }
  return utm
}

/** First-touch attribution for this browser, or null. Exposed for debugging. */
export function getFirstTouch() {
  return readJSON(FIRST_TOUCH_KEY)
}

// ---------------------------------------------------------------------------
// Transport
// ---------------------------------------------------------------------------

function authHeaders() {
  // Read straight from storage rather than importing the api module: analytics is a
  // leaf and must not depend on the API client, which already depends on this file's
  // sibling for the anonymous id.
  const token = readLocal(ACCESS_TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function send(events, { useBeacon = false } = {}) {
  if (!events.length) return

  const body = JSON.stringify({ events })

  // On page hide, fetch() is unreliable - the browser may cancel it mid-flight.
  // sendBeacon is queued by the browser and survives the navigation. It cannot set
  // an Authorization header, so those events arrive anonymous and are stitched to
  // the user by anonymous_id on the server.
  if (useBeacon) {
    try {
      if (navigator.sendBeacon) {
        const blob = new Blob([body], { type: 'application/json' })
        if (navigator.sendBeacon(ENDPOINT, blob)) return
      }
    } catch {
      /* fall through to fetch */
    }
  }

  try {
    fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body,
      keepalive: true,
      credentials: 'omit',
    }).catch(() => {
      /* analytics failures are never surfaced */
    })
  } catch {
    /* ignore */
  }
}

function flush({ useBeacon = false } = {}) {
  if (flushTimer) {
    clearTimeout(flushTimer)
    flushTimer = null
  }
  if (!queue.length) return
  const batch = queue.splice(0, queue.length)
  send(batch, { useBeacon })
}

function scheduleFlush() {
  if (flushTimer) return
  flushTimer = setTimeout(() => {
    flushTimer = null
    flush()
  }, FLUSH_INTERVAL_MS)
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Track a product event.
 *
 * @param {string} eventName  lower_snake_case, object_action (see the taxonomy).
 * @param {object} properties structured, non-sensitive detail about the action.
 *
 * Everything else - identity, session, page, referrer, UTM, timestamp - is attached
 * automatically. Never pass passwords, tokens, card details or raw user content; the
 * server strips known-sensitive keys, but the right place not to send them is here.
 */
export function trackEvent(eventName, properties = {}) {
  try {
    if (!eventName || typeof eventName !== 'string') return

    queue.push({
      event_id: randomId(),
      event_name: eventName,
      anonymous_id: getAnonymousId(),
      session_id: getSessionId(),
      timestamp: new Date().toISOString(),
      page_url: window.location.href.slice(0, 1000),
      page_path: window.location.pathname.slice(0, 500),
      page_title: (document.title || '').slice(0, 255),
      referrer: (document.referrer || '').slice(0, 1000) || null,
      ...currentUtm(),
      properties: properties && typeof properties === 'object' ? properties : {},
    })

    // Bound the queue. If the network is down, drop the oldest events rather than
    // growing memory without limit.
    if (queue.length > MAX_QUEUE) {
      queue = queue.slice(-MAX_QUEUE)
    }

    if (queue.length >= BATCH_SIZE) {
      flush()
    } else {
      scheduleFlush()
    }
  } catch {
    /* tracking must never throw into product code */
  }
}

/**
 * Track a meaningful page view.
 *
 * Called automatically on route changes. Repeat views of the same path in a row are
 * ignored, so a re-render never counts as a second view.
 */
export function trackPageView(path, pageName = null) {
  try {
    const resolved = path || window.location.pathname
    if (resolved === lastPath) return
    const previous = lastPath
    lastPath = resolved

    // Refresh attribution first: a landing with ?utm_... must be recorded before the
    // event that reports it.
    captureAttribution()

    const isLanding = resolved === '/' || resolved === '/first-page'
    const properties = {
      page_name: pageName || pageNameFor(resolved),
      path: resolved,
      previous_path: previous,
    }

    trackEvent(isLanding ? 'landing_page_viewed' : 'page_viewed', properties)

    // The auth and pricing pages are funnel steps in their own right, so they emit a
    // dedicated event as well as the generic page view.
    if (resolved === '/login') {
      trackEvent('login_page_viewed', properties)
      trackEvent('signup_page_viewed', properties)
    } else if (resolved === '/pricing') {
      trackEvent('pricing_page_viewed', properties)
    }
  } catch {
    /* ignore */
  }
}

/**
 * Track a call-to-action click.
 *
 * One event for every CTA in the product, distinguished by properties rather than by
 * inventing a separate event name per button.
 *
 * @example
 * trackCTA({ cta_id: 'hero_start_mock_interview', cta_text: 'Start Mock Interview',
 *            location: 'hero', destination: '/login' })
 */
export function trackCTA({ ctaId, ctaText, location, destination, position } = {}) {
  trackEvent('cta_clicked', {
    cta_id: ctaId,
    cta_text: ctaText ? String(ctaText).slice(0, 120) : undefined,
    location,
    destination,
    position,
    page: window.location.pathname,
  })
}

/**
 * Bind this browser's anonymous id to the now-authenticated user.
 *
 * Call immediately after a successful login or signup. The server takes the user id
 * from the bearer token, never from this call, and backfills the visitor's earlier
 * events so nothing from before the account existed is lost.
 */
export function identify(userId) {
  try {
    if (!userId) return

    // Only stitch once per user per browser - repeating it on every page load would
    // be a wasted round trip on an already-established mapping.
    if (readLocal(STITCHED_KEY) === String(userId)) return

    // Flush first so queued pre-login events are already stored under the anonymous
    // id when the stitch backfills them.
    flush()

    fetch(IDENTIFY_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ anonymous_id: getAnonymousId() }),
      credentials: 'omit',
    })
      .then(() => writeLocal(STITCHED_KEY, String(userId)))
      .catch(() => {
        /* retried on the next login */
      })
  } catch {
    /* ignore */
  }
}

/**
 * Clear the authenticated binding on logout.
 *
 * The anonymous id deliberately survives: it is the same browser, and keeping it
 * means a returning visitor is still recognised as one person across sessions.
 */
export function resetIdentity() {
  removeLocal(STITCHED_KEY)
}

/** Report a user-facing error that could plausibly cost a conversion. */
export function trackError(category, detail = {}) {
  trackEvent(category || 'frontend_error', {
    error_category: detail.category,
    feature: detail.feature,
    endpoint: detail.endpoint,
    status: detail.status,
    code: detail.code,
    page: window.location.pathname,
  })
}

function pageNameFor(path) {
  const names = {
    '/': 'landing',
    '/first-page': 'landing',
    '/features': 'features',
    '/pricing': 'pricing',
    '/about': 'about',
    '/careers': 'careers',
    '/contact': 'contact',
    '/blogs': 'blogs',
    '/help': 'help_center',
    '/login': 'login',
    '/choose-plan': 'choose_plan',
    '/checkout': 'checkout',
    '/feed': 'feed',
    '/network': 'network',
    '/jobs': 'jobs',
    '/lms': 'lms',
    '/evaluation': 'evaluation',
    '/ai-mode': 'ai_mode',
    '/ai-interviews': 'ai_interviews',
    '/notifications': 'notifications',
    '/messages': 'messages',
    '/settings': 'settings',
  }
  if (names[path]) return names[path]
  if (path.startsWith('/profile/')) return 'profile'
  if (path.startsWith('/blogs/')) return 'blog_post'
  if (path.startsWith('/post/')) return 'post_detail'
  return path.replace(/^\//, '').replace(/[^a-z0-9]+/gi, '_').toLowerCase() || 'unknown'
}

/**
 * Start automatic tracking. Called once from App on mount.
 *
 * Automatic: sessions, attribution capture, page views, flush-on-hide.
 * Manual: every meaningful business action, instrumented at the call site.
 */
export function initAnalytics() {
  if (initialised) return
  initialised = true

  try {
    getAnonymousId()
    getSessionId()
    captureAttribution()

    // Flush when the tab is hidden rather than on beforeunload, which does not fire
    // reliably on mobile. This is also the only place a beacon is used.
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        flush({ useBeacon: true })
      } else {
        getSessionId() // refresh the inactivity window
      }
    })

    window.addEventListener('pagehide', () => flush({ useBeacon: true }))
  } catch {
    /* ignore */
  }
}

export default {
  initAnalytics,
  trackEvent,
  trackPageView,
  trackCTA,
  trackError,
  identify,
  resetIdentity,
  getAnonymousId,
  getSessionId,
  getFirstTouch,
}
