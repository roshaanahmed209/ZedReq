export const PRELAUNCH_NOTICE_SESSION_KEY = 'zedreq_show_prelaunch_notice'

/** Mirrors ZedReq `PrelaunchNoticePublic` defaults if the API is unreachable. */
export const PRELAUNCH_NOTICE_FALLBACK = {
  enabled: true,
  badge_label: 'Pre-launch',
  title: 'ZedReq is not officially live yet',
  body:
    'You are using an early version of the product. Features and data may change, ' +
    'and you may occasionally run into bugs or rough edges. Thank you for trying ' +
    'ZedReq—we rely on your feedback to improve.',
  bug_email: 'zed.req@yahoo.com',
  primary_button_label: 'Continue',
  secondary_button_label: 'Email us',
  mailto_subject: 'ZedReq bug report',
}

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
