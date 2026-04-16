import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Beams from '../components/Beams'
import PlanFlowBackButton from '../components/PlanFlowBackButton'
import api from '../services/api'
import {
  PLATFORM_ACCESS_LINES,
  FREE_TEASER_WORDS,
  FREE_MONTHLY_LIMITS,
  PRO_MONTHLY_LIMITS,
  PREMIUM_MONTHLY_LIMITS,
  ENTERPRISE_USAGE_FEATURES,
} from '../constants/platformPricing'
import '../css/pages/FirstPage.css'
import '../css/pages/ChoosePlan.css'

const ChoosePlan = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showFreePlanActive, setShowFreePlanActive] = useState(false)

  const goToFeed = () => navigate('/feed', { replace: true })

  useEffect(() => {
    if (!showFreePlanActive) return undefined
    const t = setTimeout(() => navigate('/feed', { replace: true }), 2800)
    return () => clearTimeout(t)
  }, [showFreePlanActive, navigate])

  const selectFree = async () => {
    setError('')
    setLoading(true)
    try {
      await api.put('/api/user/subscription', { plan: 'free' })
      setShowFreePlanActive(true)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not select Free plan')
    } finally {
      setLoading(false)
    }
  }

  const feature = (text, emph = false) => (
    <li className={`pricing__feature${emph ? ' pricing__feature--emph' : ''}`}>
      <i className="f-yes" aria-label="Included" />
      {text}
    </li>
  )

  return (
    <div className="choose-plan-page">
      {showFreePlanActive && (
        <div className="choose-plan-success-overlay" role="status" aria-live="polite">
          <div className="choose-plan-success-card">
            <p className="choose-plan-success-title">You&apos;re on the Free plan</p>
            <p className="choose-plan-success-body">
              Your plan is active. You can upgrade anytime from Settings. Taking you to your feed…
            </p>
            <button type="button" className="btn btn--accent choose-plan-success-cta" onClick={goToFeed}>
              Go to feed now
            </button>
          </div>
        </div>
      )}
      <PlanFlowBackButton />
      <section className="pricing choose-plan-pricing" style={{ position: 'relative', overflow: 'hidden' }}>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: 0,
            opacity: 0.55,
          }}
        >
          <Beams
            beamWidth={1.5}
            beamHeight={25}
            beamNumber={40}
            speed={3.1}
            noiseIntensity={2.4}
            scale={0.29}
            rotation={45}
            lightColor="#1585A1"
          />
        </div>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'rgba(0, 0, 0, 0.45)',
            zIndex: 1,
            pointerEvents: 'none',
          }}
        />
        <div className="choose-plan-pricing__inner">
          <div className="pricing__head">
            <p className="pricing__eyebrow">Billing</p>
            <h1 className="pricing__hl" id="choose-plan-hl">
              Choose your<br /><em>plan</em>
            </h1>
          </div>
          <p className="choose-plan__lead">
            Pick a plan to continue using ZedReq. Networking, jobs, feed &amp; messaging are unlimited; AI Mode, LMS
            enrollments &amp; mock interviews follow monthly quotas (reset 1st of month, UTC).
          </p>
          {error && <div className="choose-plan-error">{error}</div>}

          <div className="pricing__grid choose-plan__grid">
            {/* Free */}
            <div className="pricing__card">
              <p className="pricing__tier">Free</p>
              <p className="choose-plan__card-desc">
                Default plan for new accounts — explore AI career tools within platform limits.
              </p>
              <p className="pricing__price">$0</p>
              <p className="pricing__period">per month</p>
              <hr className="pricing__rule" />
              <ul className="pricing__features pricing__teaser">
                {FREE_TEASER_WORDS.map((word) => (
                  <li key={word} className="pricing__feature pricing__teaser-word">
                    <i className="f-yes" aria-label="Included" />
                    {word}
                  </li>
                ))}
              </ul>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">LIMITED USAGE</p>
              <ul className="pricing__features">
                {FREE_MONTHLY_LIMITS.map((line) => feature(line, true))}
              </ul>
              <button
                type="button"
                className="btn btn--outline pricing__cta"
                onClick={selectFree}
                disabled={loading}
              >
                {loading ? 'Saving…' : 'Continue with Free'}
              </button>
            </div>

            {/* Pro */}
            <div className="pricing__card pricing__card--feat">
              <span className="pricing__badge">Most popular</span>
              <p className="pricing__tier">Pro</p>
              <p className="choose-plan__card-desc choose-plan__card-desc--on-light">
                Higher quotas for AI mode, learning, and mock interviews.
              </p>
              <p className="pricing__price">$49.99</p>
              <p className="pricing__period">per month</p>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">Platform access:</p>
              <ul className="pricing__features">
                {PLATFORM_ACCESS_LINES.map((line) => feature(line))}
              </ul>
              <p className="mono-label pricing__block-label">Higher monthly limits</p>
              <ul className="pricing__features">
                {PRO_MONTHLY_LIMITS.map((line, i) => feature(line, i < 3))}
              </ul>
              <Link to="/checkout?plan=pro" className="btn pricing__cta">
                Checkout
              </Link>
            </div>

            {/* Premium */}
            <div className="pricing__card">
              <p className="pricing__tier">Premium</p>
              <p className="choose-plan__card-desc">
                Maximum standard quotas before unlimited enterprise access.
              </p>
              <p className="pricing__price">$89.99</p>
              <p className="pricing__period">per month</p>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">Platform access:</p>
              <ul className="pricing__features">
                {PLATFORM_ACCESS_LINES.map((line) => feature(line))}
              </ul>
              <p className="mono-label pricing__block-label">Highest standard monthly limits</p>
              <ul className="pricing__features">
                {PREMIUM_MONTHLY_LIMITS.map((line, i) => feature(line, i < 3))}
              </ul>
              <Link to="/checkout?plan=premium" className="btn btn--outline pricing__cta">
                Checkout
              </Link>
            </div>

            {/* Enterprise */}
            <div className="pricing__card">
              <p className="pricing__tier">Enterprise</p>
              <p className="choose-plan__card-desc">
                Unlimited usage for AI messages, courses, and interviews — assigned by agreement.
              </p>
              <p className="pricing__price">Custom</p>
              <p className="pricing__period">by arrangement</p>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">Platform access:</p>
              <ul className="pricing__features">
                {PLATFORM_ACCESS_LINES.map((line) => feature(line))}
              </ul>
              <p className="mono-label pricing__block-label">Enterprise usage</p>
              <ul className="pricing__features">
                {ENTERPRISE_USAGE_FEATURES.map(({ text, emph }) => feature(text, emph))}
              </ul>
              <Link to="/enterprise-inquiry" className="btn btn--outline pricing__cta">
                Contact us
              </Link>
            </div>
          </div>

          <p className="choose-plan__footnote">
            Limits are enforced server-side per plan. Enterprise is available by arrangement. Security and privacy practices
            are described in our <Link to="/privacy">Privacy Policy</Link> and <Link to="/terms">Terms of Use</Link>.
          </p>
        </div>
      </section>
    </div>
  )
}

export default ChoosePlan
