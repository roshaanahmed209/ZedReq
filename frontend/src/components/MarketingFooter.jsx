import React from 'react'
import { MARKETING_FOOTER_LINKS } from '../constants/marketingNav'

const A = (file) => `${import.meta.env.BASE_URL}assets/${file}`

export default function MarketingFooter() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <a href="/" aria-label="ZedReq home">
          <img src={A('logo_tr1.svg')} alt="ZedReq" className="footer__logo" />
        </a>

        <nav className="footer__nav" aria-label="Footer navigation">
          {MARKETING_FOOTER_LINKS.map((l) => (
            <a key={l.label} href={l.href} className="footer__link">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="footer__legal">
          <p>&copy; {new Date().getFullYear()} ZedReq Ltd. All rights reserved.</p>
          <p>
            <a href="/privacy" className="footer__link">
              Privacy Policy
            </a>
            {' · '}
            <a href="/terms" className="footer__link">
              Terms of Service
            </a>
          </p>
        </div>
      </div>
    </footer>
  )
}
