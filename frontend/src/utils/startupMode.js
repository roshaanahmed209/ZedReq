/**
 * Startup mode — build-time feature flag from vite.config.js `define`.
 *
 * When true: marketing/checkout UI shows only the Free tier card.
 * When false (default): all plan tiers are visible.
 *
 * This controls UI visibility only — not entitlements or billing policy.
 * Server-side quota enforcement and subscription rules remain authoritative.
 * Full billing enforcement when startup mode is active requires a future
 * backend STARTUP_STATUS flag and API guards.
 *
 * Not user-controllable at runtime (no URL params, localStorage, or debug toggles).
 */
export function isStartupMode() {
  return import.meta.env.VITE_STARTUP_STATUS === true
}
