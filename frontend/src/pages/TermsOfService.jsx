import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { LegalTermsBody } from '../content/LegalTermsBody'
import '../css/pages/GetStarted.css'

export default function TermsOfService() {
  return (
    <PublicSubpageLayout title="Terms of Use">
      <article className="get-started-modal-body public-legal-article">
        <LegalTermsBody />
      </article>
    </PublicSubpageLayout>
  )
}
