import React from 'react'
import { Link } from 'react-router-dom'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import PricingPlansGrid from '../components/PricingPlansGrid'
import { sitePath } from '../config/siteUrl'

export default function PricingPublic() {
  return (
    <PublicSubpageLayout
      title="Pricing"
      preFooter={
        <section className="pricing-section" aria-labelledby="pricing-plans-heading">
          <PricingPlansGrid instantReveal />
        </section>
      }
    >
      <div className="public-subpage-prose">
        <p>
          ZedReq offers Free, Pro, Premium, and Enterprise plans. Networking, jobs, feed, and messaging are available across plans; AI Mode, LMS enrollments, and mock interviews follow monthly quotas that reset on the 1st of each month (UTC).
        </p>
        <p>
          Compare plans and limits below, or open checkout after signing in to subscribe.
        </p>
        <p>
          Enterprise plans include unlimited usage for AI, courses, and interviews by agreement—use Contact us on the Enterprise card below.
        </p>
        <p>
          Details on data use: <a href={sitePath('/privacy')}>Privacy Policy</a>
          {' · '}
          <a href={sitePath('/terms')}>Terms of Use</a>.
        </p>
        <p className="public-subpage-inline-links">
          <a href="#pricing-plans-heading">Jump to plans</a>
          {' · '}
          <Link to="/get-started">Create free profile</Link>
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
