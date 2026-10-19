import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { ZEDREQ_EMAIL, zedreqMailto } from '../config/contact'

export default function Contact() {
  return (
    <PublicSubpageLayout title="Contact">
      <div className="public-subpage-prose">
        <p>For support, account questions, and privacy-related requests:</p>
        <p>
          <a href={zedreqMailto()}>{ZEDREQ_EMAIL}</a>
        </p>
        <p>We aim to respond within a few business days.</p>
      </div>
    </PublicSubpageLayout>
  )
}
