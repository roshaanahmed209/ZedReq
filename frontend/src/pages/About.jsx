import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'

export default function About() {
  return (
    <PublicSubpageLayout title="About ZedReq">
      <div className="public-subpage-prose">
        <p>
          ZedReq is an AI-powered career platform focused on fair, useful matching and preparation—not generic job boards. We build tools for job seekers and professionals who want structured feedback, privacy-aware design, and features that respect how hiring actually works.
        </p>
        <p>
          Our team works on matching, learning, interviews, and trust &amp; safety so the product stays accurate, secure, and aligned with user expectations.
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
