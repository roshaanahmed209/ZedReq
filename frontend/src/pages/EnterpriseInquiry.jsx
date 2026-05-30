import React, { useEffect, useRef, useState, useCallback } from 'react'
import { Link, useNavigate, Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import PlanFlowBackButton from '../components/PlanFlowBackButton'
import { isStartupMode } from '../utils/startupMode'
import '../css/pages/EnterpriseInquiry.css'

const EnterpriseInquiry = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [freeLoading, setFreeLoading] = useState(false)
  const [error, setError] = useState('')
  const [thankYouReveal, setThankYouReveal] = useState(false)
  const thankYouRef = useRef(null)

  useEffect(() => {
    if (user?.email) {
      setEmail(user.email)
    }
  }, [user?.email])

  // After submit: smooth scroll first; only when scroll has settled, show + animate thank-you text
  useEffect(() => {
    if (!submitted) {
      setThankYouReveal(false)
      return
    }

    const section = thankYouRef.current
    if (!section) return

    let fallbackTimer
    let done = false

    const reveal = () => {
      if (done) return
      done = true
      setThankYouReveal(true)
      section.focus?.()
    }

    const runScroll = () => {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    requestAnimationFrame(() => {
      requestAnimationFrame(runScroll)
    })

    const onScrollEnd = () => reveal()

    window.addEventListener('scrollend', onScrollEnd, { passive: true })
    // scrollend is not in all browsers; smooth scroll ~400–900ms depending on distance
    fallbackTimer = window.setTimeout(reveal, 1100)

    return () => {
      window.removeEventListener('scrollend', onScrollEnd)
      window.clearTimeout(fallbackTimer)
    }
  }, [submitted])

  const continueWithFree = useCallback(async () => {
    setError('')
    setFreeLoading(true)
    try {
      const billing_email = (email || user?.email || '').trim()
      const body = { plan: 'free' }
      if (billing_email) body.billing_email = billing_email
      await api.put('/api/user/subscription', body)
      navigate('/feed', { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Could not switch to Free plan')
    } finally {
      setFreeLoading(false)
    }
  }, [navigate, email, user?.email])

  if (isStartupMode()) {
    return <Navigate to="/choose-plan" replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/api/user/enterprise-inquiry', { email: email.trim() })
      setSubmitted(true)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="enterprise-inquiry-page">
      <PlanFlowBackButton to="choose-plan" />
      <section className="enterprise-hero" aria-label="Enterprise inquiry form">
        <h1 className="enterprise-title">Enterprise</h1>
        <p className="enterprise-lead">
          Tell us how to reach you. Our team will follow up about unlimited usage, security, and onboarding.
        </p>

        {error && <p className="enterprise-error" role="alert">{error}</p>}

        <form className="enterprise-form" onSubmit={handleSubmit}>
          <label className="enterprise-label" htmlFor="enterprise-email">
            Work email
          </label>
          <input
            id="enterprise-email"
            className="enterprise-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="you@company.com"
          />
          <button className="enterprise-submit" type="submit" disabled={loading}>
            {loading ? 'Sending…' : 'Submit'}
          </button>
        </form>

        <Link className="enterprise-back" to="/choose-plan">
          ← Back to plans
        </Link>
      </section>

      <div className="enterprise-scroll-anchor" aria-hidden="true" />

      {submitted && (
        <section
          ref={thankYouRef}
          tabIndex={-1}
          className="enterprise-thankyou"
          aria-live="polite"
        >
          <div
            className={
              thankYouReveal
                ? 'enterprise-thankyou-content enterprise-thankyou-content--visible'
                : 'enterprise-thankyou-content'
            }
            aria-hidden={!thankYouReveal}
          >
            <h2 className="enterprise-thankyou-headline enterprise-thankyou-reveal-line enterprise-thankyou-reveal-line--headline">
              Thank you
            </h2>
            <p className="enterprise-thankyou-detail enterprise-thankyou-reveal-line enterprise-thankyou-reveal-line--body1">
              We&apos;ve received your request. A member of the ZedReq team will contact you shortly.
            </p>
            <p className="enterprise-thankyou-detail enterprise-thankyou-reveal-line enterprise-thankyou-reveal-line--body2">
              You can continue with a <strong>Free</strong> plan to explore the platform while you wait.
            </p>
            <div className="enterprise-thankyou-actions enterprise-thankyou-reveal-line enterprise-thankyou-reveal-line--actions">
              <button
                type="button"
                className="enterprise-btn-free"
                onClick={continueWithFree}
                disabled={freeLoading}
              >
                {freeLoading ? 'Switching…' : 'Continue with Free'}
              </button>
              <Link className="enterprise-btn-plans" to="/choose-plan">
                Back to plans
              </Link>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

export default EnterpriseInquiry
