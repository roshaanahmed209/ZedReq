import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { ZEDREQ_EMAIL, zedreqMailto } from '../config/contact'

export default function Careers() {
  return (
    <PublicSubpageLayout title="Careers">
      <div className="public-subpage-prose">
        <p>
          We do not always have open roles listed publicly. If you are interested in product engineering, ML/AI, design, or go-to-market around career tech, we would like to hear from you.
        </p>
        <p>
          Send a short note and link to your work or profile: <a href={zedreqMailto()}>{ZEDREQ_EMAIL}</a>
        </p>
      </div>
    </PublicSubpageLayout>
  )
}
