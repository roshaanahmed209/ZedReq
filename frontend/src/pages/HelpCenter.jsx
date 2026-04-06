import React from 'react'
import { Link } from 'react-router-dom'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { sitePath } from '../config/siteUrl'
import { ZEDREQ_EMAIL, zedreqMailto } from '../config/contact'

export default function HelpCenter() {
  return (
    <PublicSubpageLayout title="Help Center">
      <div className="public-subpage-prose">
        <p>Quick links:</p>
        <ul>
          <li><Link to="/get-started">Create an account</Link></li>
          <li><Link to="/contact">Contact support</Link></li>
          <li><a href={sitePath('/privacy')}>Privacy Policy</a></li>
          <li><a href={sitePath('/terms')}>Terms of Use</a></li>
        </ul>
        <p>
          For billing or plan changes, use in-app settings after you sign in, or email <a href={zedreqMailto()}>{ZEDREQ_EMAIL}</a>.
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
