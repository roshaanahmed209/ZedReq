import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Beams from '../components/Beams'
import PlanFlowBackButton from '../components/PlanFlowBackButton'
import api from '../services/api'
import '../css/pages/FirstPage.css'
import '../css/pages/ChoosePlan.css'

const ChoosePlan = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const selectFree = async () => {
    setError('')
    setLoading(true)
    try {
      await api.put('/api/user/subscription', { plan: 'free' })
      navigate('/feed', { replace: true })
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Could not select Free plan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="choose-plan-page">
      <PlanFlowBackButton />
      <section className="pricing-section choose-plan-pricing" style={{ position: 'relative', overflow: 'hidden' }}>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            zIndex: 0,
            opacity: 0.6,
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
            lightColor="#00b4d8"
          />
        </div>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'rgba(13, 13, 13, 0.3)',
            zIndex: 1,
            pointerEvents: 'none',
          }}
        />
        <div style={{ position: 'relative', zIndex: 2 }}>
          <h2 className="section-title scroll-reveal visible">Choose your plan</h2>
          <p className="pricing-subtitle scroll-reveal visible">
            Pick a plan to continue using ZedReq. Networking, jobs, feed &amp; messaging are unlimited; AI Mode, LMS
            enrollments &amp; mock interviews follow monthly quotas (reset 1st of month, UTC).
          </p>
          {error && <div className="choose-plan-error">{error}</div>}
          <div className="pricing-grid">
            {/* Free */}
            <div className="pricing-card scroll-reveal-scale visible">
              <div className="pricing-card-header">
                <h3>Free</h3>
                <p className="pricing-card-desc">Default plan for new accounts — explore AI career tools within platform limits.</p>
              </div>
              <div className="price">
                $0<span className="price-period">/month</span>
              </div>
              <button
                type="button"
                className="btn-primary pricing-btn"
                onClick={selectFree}
                disabled={loading}
              >
                {loading ? 'Saving…' : 'Continue with Free'}
              </button>
              <div className="pricing-divider" />
              <p className="pricing-includes">Platform access (no extra cap):</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Unlimited professional networking &amp; connections
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Unlimited job discovery, saved roles &amp; applications
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Personalized feed, posts &amp; community engagement
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Direct messaging with your network
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  AI-powered job matching &amp; recommendations
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Skills evaluation &amp; career gap insights
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Smart profile, portfolio &amp; visibility controls
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Notifications, alerts &amp; in-app updates
                </li>
              </ul>
              <p className="pricing-includes">Monthly usage limits (AI, learning &amp; interviews):</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  30 AI assistant (AI Mode) messages per month
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  2 LMS course enrollments per month
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  1 AI mock interview session per month
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Up to 60 seconds per interview session
                </li>
              </ul>
            </div>

            {/* Pro */}
            <div className="pricing-card featured scroll-reveal-scale visible">
              <span className="badge">Most popular</span>
              <div className="pricing-card-header">
                <h3>Pro</h3>
                <p className="pricing-card-desc">Higher quotas for AI mode, learning, and mock interviews.</p>
              </div>
              <div className="price">
                $49<span className="price-period">.99/month</span>
              </div>
              <Link to="/checkout?plan=pro" className="btn-primary pricing-btn">
                Checkout
              </Link>
              <div className="pricing-divider" />
              <p className="pricing-includes">Everything in Free — unlimited networking, jobs, feed, messaging &amp; more</p>
              <p className="pricing-includes">Higher monthly limits:</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  100 AI assistant (AI Mode) messages per month
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  3 LMS course enrollments per month
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  3 AI mock interview sessions per month
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Up to 60 seconds per interview session
                </li>
              </ul>
            </div>

            {/* Premium */}
            <div className="pricing-card scroll-reveal-scale visible">
              <div className="pricing-card-header">
                <h3>Premium</h3>
                <p className="pricing-card-desc">Maximum standard quotas before unlimited enterprise access.</p>
              </div>
              <div className="price">
                $89<span className="price-period">.99/month</span>
              </div>
              <Link to="/checkout?plan=premium" className="btn-primary pricing-btn">
                Checkout
              </Link>
              <div className="pricing-divider" />
              <p className="pricing-includes">Everything in Free — unlimited networking, jobs, feed, messaging &amp; more</p>
              <p className="pricing-includes">Highest standard monthly limits:</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  500 AI assistant (AI Mode) messages per month
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  5 LMS course enrollments per month
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  5 AI mock interview sessions per month
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Up to 60 seconds per interview session
                </li>
              </ul>
            </div>

            {/* Enterprise */}
            <div className="pricing-card scroll-reveal-scale visible">
              <div className="pricing-card-header">
                <h3>Enterprise</h3>
                <p className="pricing-card-desc">Unlimited usage for AI messages, courses, and interviews — assigned by agreement.</p>
              </div>
              <div className="price">Custom</div>
              <Link to="/enterprise-inquiry" className="btn-secondary pricing-btn">
                Contact us
              </Link>
              <div className="pricing-divider" />
              <p className="pricing-includes">Everything in Free — unlimited networking, jobs, feed, messaging &amp; more</p>
              <p className="pricing-includes">Enterprise usage:</p>
              <ul className="pricing-features">
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Unlimited AI assistant (AI Mode) messages
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Unlimited LMS course enrollments
                </li>
                <li className="pricing-feature-item included highlight">
                  <span className="pricing-check">✓</span>
                  Unlimited AI mock interview sessions
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Up to 10 minutes per interview session
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Plan assigned by ZedReq admin (super admin)
                </li>
                <li className="pricing-feature-item included">
                  <span className="pricing-check">✓</span>
                  Custom onboarding &amp; account support by agreement
                </li>
              </ul>
            </div>
          </div>
          <p className="pricing-note scroll-reveal visible">
            Limits are enforced server-side per plan. Enterprise is available by arrangement. Security and privacy practices
            are described in our Privacy Policy.
          </p>
        </div>
      </section>
    </div>
  )
}

export default ChoosePlan
