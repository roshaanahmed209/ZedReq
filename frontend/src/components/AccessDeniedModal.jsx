import React, { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAccessDeniedModalState } from '../contexts/AccessDeniedModalContext'
import { userAPI } from '../services/api'
import {
  FEATURE_LABELS,
  formatPlanName,
  formatUsageLine,
  usagePercent,
} from '../utils/accessDenied'
import { isStartupMode } from '../utils/startupMode'
import '../css/components/AccessDeniedModal.css'

const FEATURE_ORDER = ['ai_messages', 'course_enrollments', 'interview_sessions']

function UsageMeter({ label, used, limit, highlight }) {
  const isUnlimited = limit === -1
  const pct = usagePercent(used, limit)
  const exhausted = !isUnlimited && limit > 0 && (used ?? 0) >= limit

  return (
    <div className={`access-denied-meter${highlight ? ' access-denied-meter--highlight' : ''}`}>
      <div className="access-denied-meter__head">
        <span className="access-denied-meter__label">{label}</span>
        <span
          className={`access-denied-meter__value${exhausted ? ' access-denied-meter__value--exhausted' : ''}`}
        >
          {formatUsageLine(used, limit)}
        </span>
      </div>
      {!isUnlimited && (
        <div className="access-denied-meter__track" aria-hidden>
          <div
            className={`access-denied-meter__fill${exhausted ? ' access-denied-meter__fill--exhausted' : ''}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
      <p className="access-denied-meter__hint">
        {isUnlimited
          ? 'Unlimited on your plan'
          : exhausted
            ? 'Limit reached this month'
            : `${Math.max(0, limit - (used ?? 0))} remaining this month`}
      </p>
    </div>
  )
}

export default function AccessDeniedModal() {
  const { modal, closeAccessDeniedModal } = useAccessDeniedModalState()
  const closeRef = useRef(null)
  const [usageSummary, setUsageSummary] = useState(null)
  const [usageLoading, setUsageLoading] = useState(false)

  const { isOpen, payload } = modal
  const isQuota = payload?.type === 'quota'

  const title = isQuota ? 'Monthly limit reached' : 'Access denied'

  const planLabel = useMemo(() => {
    const plan =
      usageSummary?.plan?.plan_name || payload?.plan || null
    return formatPlanName(plan)
  }, [usageSummary, payload?.plan])

  useEffect(() => {
    if (!isOpen) {
      setUsageSummary(null)
      return undefined
    }

    const prevOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeRef.current?.focus()

    const onKeyDown = (e) => {
      if (e.key === 'Escape') closeAccessDeniedModal()
    }
    window.addEventListener('keydown', onKeyDown)

    setUsageLoading(true)
    userAPI
      .getSubscriptionUsage()
      .then((res) => setUsageSummary(res.data))
      .catch(() => setUsageSummary(null))
      .finally(() => setUsageLoading(false))

    return () => {
      document.body.style.overflow = prevOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [isOpen, closeAccessDeniedModal])

  if (!isOpen || !payload) return null

  const usage = usageSummary?.usage || {}
  const showUpgrade = !isStartupMode() && payload.plan !== 'enterprise'

  return (
    <div
      className="access-denied-overlay"
      role="presentation"
      onClick={closeAccessDeniedModal}
    >
      <div
        className="access-denied-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="access-denied-title"
        aria-describedby="access-denied-desc"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          className="access-denied-close"
          aria-label="Close"
          onClick={closeAccessDeniedModal}
        >
          ×
        </button>

        <div className="access-denied-badge">
          {isQuota ? 'Plan limit' : 'Restricted'}
        </div>

        <h2 id="access-denied-title" className="access-denied-title">
          {title}
        </h2>

        <p id="access-denied-desc" className="access-denied-message">
          {payload.message}
        </p>

        {planLabel ? (
          <p className="access-denied-plan">
            Current plan: <strong>{planLabel}</strong>
          </p>
        ) : null}

        <div className="access-denied-usage">
          <h3 className="access-denied-usage__title">Monthly usage</h3>
          <p className="access-denied-usage__note">
            Quotas reset on the 1st of each month (UTC).
          </p>

          {usageLoading ? (
            <p className="access-denied-usage__loading">Loading usage…</p>
          ) : (
            FEATURE_ORDER.map((featureKey) => {
              const fromApi = usage[featureKey]
              const isAffected = payload.feature === featureKey
              const used = isAffected && payload.used != null ? payload.used : fromApi?.used
              const limit =
                isAffected && payload.limit != null ? payload.limit : fromApi?.limit

              if (used == null && limit == null && !fromApi) {
                return null
              }

              return (
                <UsageMeter
                  key={featureKey}
                  label={FEATURE_LABELS[featureKey]}
                  used={used ?? 0}
                  limit={limit ?? 0}
                  highlight={isAffected}
                />
              )
            })
          )}
        </div>

        <div className="access-denied-actions">
          <button
            ref={closeRef}
            type="button"
            className="access-denied-btn access-denied-btn-secondary"
            onClick={closeAccessDeniedModal}
          >
            Close
          </button>
          {showUpgrade ? (
            <Link
              to="/choose-plan"
              className="access-denied-btn access-denied-btn-primary"
              onClick={closeAccessDeniedModal}
            >
              Upgrade plan
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  )
}
