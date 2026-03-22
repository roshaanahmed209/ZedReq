import React from 'react'
import PublicSubpageLayout from '../components/PublicSubpageLayout'
import { LegalCookieBody } from '../content/LegalCookieBody'
import '../css/pages/GetStarted.css'

export default function CookiePolicy() {
  return (
    <PublicSubpageLayout title="Cookie Policy">
      <article className="get-started-modal-body public-legal-article">
        <LegalCookieBody />
      </article>
    </PublicSubpageLayout>
  )
}
