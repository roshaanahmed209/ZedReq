import React, { useEffect, useRef } from 'react'
import '../css/components/PrelaunchNoticeModal.css'

const BUG_EMAIL = 'zed.req@yahoo.com'
const MAILTO_SUBJECT = encodeURIComponent('ZedReq bug report')
const MAILTO_HREF = `mailto:${BUG_EMAIL}?subject=${MAILTO_SUBJECT}`

export default function PrelaunchNoticeModal({ onDismiss }) {
  const primaryRef = useRef(null)

  useEffect(() => {
    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    primaryRef.current?.focus()

    const onKeyDown = (e) => {
      if (e.key === 'Escape') onDismiss()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = prevOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [onDismiss])

  return (
    <div
      className="prelaunch-notice-overlay"
      role="presentation"
      onClick={onDismiss}
    >
      <div
        className="prelaunch-notice-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="prelaunch-notice-title"
        aria-describedby="prelaunch-notice-desc"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="prelaunch-notice-badge">Pre-launch</div>
        <h2 id="prelaunch-notice-title" className="prelaunch-notice-title">
          ZedReq is not officially live yet
        </h2>
        <p id="prelaunch-notice-desc" className="prelaunch-notice-body">
          You are using an early version of the product. Features and data may change,
          and you may occasionally run into bugs or rough edges. Thank you for trying
          ZedReq—we rely on your feedback to improve.
        </p>
        <div className="prelaunch-notice-email-row">
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden
          >
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
            <polyline points="22,6 12,13 2,6" />
          </svg>
          <div>
            <div className="prelaunch-notice-email-label">Report bugs</div>
            <a className="prelaunch-notice-email-link" href={MAILTO_HREF}>
              {BUG_EMAIL}
            </a>
          </div>
        </div>
        <div className="prelaunch-notice-actions">
          <a className="prelaunch-notice-btn prelaunch-notice-btn-secondary" href={MAILTO_HREF}>
            Email us
          </a>
          <button
            ref={primaryRef}
            type="button"
            className="prelaunch-notice-btn prelaunch-notice-btn-primary"
            onClick={onDismiss}
          >
            Continue
          </button>
        </div>
      </div>
    </div>
  )
}
