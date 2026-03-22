import React from 'react'
import { Link } from 'react-router-dom'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { sitePath } from '../config/siteUrl'

export default function PricingPublic() {
  return (
    <PublicSubpageLayout title="Pricing">
      <div className="public-subpage-prose">
        <p>
          ZedReq offers Free, Pro, Premium, and Enterprise plans. Networking, jobs, feed, and messaging are available across plans; AI Mode, LMS enrollments, and mock interviews follow monthly quotas that reset on the 1st of each month (UTC).
        </p>
        <p>
          See current plans and limits on the home page, or open checkout after signing in to subscribe.
        </p>
        <p>
          Enterprise plans include unlimited usage for AI, courses, and interviews by agreement—contact us from the pricing section on the home page.
        </p>
        <p>
          Details on data use: <a href={sitePath('/privacy')}>Privacy Policy</a>.
        </p>
        <p className="public-subpage-inline-links">
          <Link to="/">View pricing on home</Link>
          {' · '}
          <Link to="/get-started">Create free profile</Link>
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
