export const PRELAUNCH_NOTICE_SESSION_KEY = 'zedreq_show_prelaunch_notice'

export function markPrelaunchNoticePending() {
  try {
    sessionStorage.setItem(PRELAUNCH_NOTICE_SESSION_KEY, '1')
  } catch {
    /* ignore */
  }
}

export function isPrelaunchNoticePending() {
  try {
    return sessionStorage.getItem(PRELAUNCH_NOTICE_SESSION_KEY) === '1'
  } catch {
    return false
  }
}

export function clearPrelaunchNoticePending() {
  try {
    sessionStorage.removeItem(PRELAUNCH_NOTICE_SESSION_KEY)
  } catch {
    /* ignore */
  }
}
