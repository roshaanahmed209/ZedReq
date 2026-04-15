import React from 'react'
import { Link } from 'react-router-dom'
import '../css/pages/FirstPage.css'

/**
 * Shared pricing cards + copy (matches home #pricing).
 * @param {boolean} instantReveal — add `visible` for pages without FirstPage scroll-reveal observer
 */
export default function PricingPlansGrid({ instantReveal = false }) {
  const rev = (cls) => (instantReveal ? `${cls} visible` : cls)

  return (
    <>
      <h2 id="pricing-plans-heading" className={rev('section-title scroll-reveal')}>
        Simple, Transparent Pricing
      </h2>
      <p className={rev('pricing-subtitle scroll-reveal')}>
        Plans match subscription tiers in ZedReq. Networking, jobs, feed &amp; messaging are unlimited; AI Mode, LMS
        enrollments &amp; mock interviews follow monthly quotas (reset 1st of month, UTC).
      </p>
      <div className="pricing-grid">
        <div className={rev('pricing-card scroll-reveal-scale')}>
          <div className="pricing-card-header">
            <h3>Free</h3>
            <p className="pricing-card-desc">Default plan for new accounts — explore AI career tools within platform limits.</p>
          </div>
          <div className="price">
            $0<span className="price-period">/month</span>
          </div>
          <Link to="/login" className="btn-primary pricing-btn">
            Get started
          </Link>
          <div className="pricing-divider" />
          <p className="pricing-includes">Platform access:</p>
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
          <p className="pricing-includes">LIMITED USAGE</p>
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

        <div className={rev('pricing-card featured scroll-reveal-scale')}>
          <span className="badge">Most popular</span>
          <div className="pricing-card-header">
            <h3>Pro</h3>
            <p className="pricing-card-desc">Higher quotas for AI mode, learning, and mock interviews.</p>
          </div>
          <div className="price">
            $49<span className="price-period">.99/month</span>
          </div>
          <Link to="/login" className="btn-primary pricing-btn">
            Subscribe
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

        <div className={rev('pricing-card scroll-reveal-scale')}>
          <div className="pricing-card-header">
            <h3>Premium</h3>
            <p className="pricing-card-desc">Maximum standard quotas before unlimited enterprise access.</p>
          </div>
          <div className="price">
            $89<span className="price-period">.99/month</span>
          </div>
          <Link to="/login" className="btn-primary pricing-btn">
            Subscribe
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

        <div className={rev('pricing-card scroll-reveal-scale')}>
          <div className="pricing-card-header">
            <h3>Enterprise</h3>
            <p className="pricing-card-desc">Unlimited usage for AI messages, courses, and interviews — assigned by agreement.</p>
          </div>
          <div className="price">Custom</div>
          <Link to="/login" className="btn-secondary pricing-btn">
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
      <p className={rev('pricing-note scroll-reveal')}>
        Limits are enforced server-side per plan. Enterprise is available by arrangement. Security and privacy practices are described in our{' '}
        <Link to="/privacy">Privacy Policy</Link> and <Link to="/terms">Terms of Use</Link>.
      </p>
    </>
  )
}
