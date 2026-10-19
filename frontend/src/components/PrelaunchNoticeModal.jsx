import React, { useEffect, useMemo, useRef } from 'react'
import '../css/components/PrelaunchNoticeModal.css'

export default function PrelaunchNoticeModal({ config, onDismiss }) {
  const primaryRef = useRef(null)

  const mailtoHref = useMemo(() => {
    const email = (config?.bug_email || '').trim()
    const sub = encodeURIComponent(config?.mailto_subject || 'ZedReq bug report')
    if (!email) return '#'
    return `mailto:${email}?subject=${sub}`
  }, [config?.bug_email, config?.mailto_subject])

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

  const badge = config?.badge_label ?? 'Pre-launch'
  const title = config?.title ?? ''
  const body = config?.body ?? ''
  const primaryLabel = config?.primary_button_label ?? 'Continue'
  const secondaryLabel = config?.secondary_button_label ?? 'Email us'
  const bugEmail = config?.bug_email ?? ''

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
        <div className="prelaunch-notice-badge">{badge}</div>
        <h2 id="prelaunch-notice-title" className="prelaunch-notice-title">
          {title}
        </h2>
        <p id="prelaunch-notice-desc" className="prelaunch-notice-body">
          {body}
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
            <a className="prelaunch-notice-email-link" href={mailtoHref}>
              {bugEmail}
            </a>
          </div>
        </div>
        <div className="prelaunch-notice-actions">
          <a
            className="prelaunch-notice-btn prelaunch-notice-btn-secondary"
            href={mailtoHref}
          >
            {secondaryLabel}
          </a>
          <button
            ref={primaryRef}
            type="button"
            className="prelaunch-notice-btn prelaunch-notice-btn-primary"
            onClick={onDismiss}
          >
            {primaryLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
