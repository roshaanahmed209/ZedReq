import React from 'react'
import { Link } from 'react-router-dom'
import PublicSubpageLayout from '../components/PublicSubpageLayout'

export default function Features() {
  return (
    <PublicSubpageLayout title="Features">
      <div className="public-subpage-prose">
        <p>
          ZedReq combines AI job matching, a career assistant, mock interviews, networking, and learning tools in one platform—built to help you find the right role and prepare with confidence.
        </p>
        <ul>
          <li>AI job matching from your profile and goals</li>
          <li>Career assistant for applications and refinement</li>
          <li>Realistic mock interviews with structured feedback</li>
          <li>Networking, jobs feed, and LMS-style learning</li>
        </ul>
        <p>
          For the full interactive overview, visit the home page or create a free profile to try the product.
        </p>
        <p className="public-subpage-inline-links">
          <Link to="/">Back to home</Link>
          {' · '}
          <Link to="/get-started">Get started</Link>
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
