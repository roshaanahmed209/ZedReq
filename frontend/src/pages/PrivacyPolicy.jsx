import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { LegalPrivacyBody } from '../content/LegalPrivacyBody'
import '../css/pages/GetStarted.css'

export default function PrivacyPolicy() {
  return (
    <PublicSubpageLayout title="Privacy Policy">
      <article className="get-started-modal-body public-legal-article">
        <LegalPrivacyBody />
      </article>
    </PublicSubpageLayout>
  )
}
