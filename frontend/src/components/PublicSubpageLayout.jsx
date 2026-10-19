import React from 'react'
import MarketingShell from './MarketingShell'
import '../css/pages/PublicSubpage.css'

export default function PublicSubpageLayout({
  title,
  children,
  mainClassName = '',
  preFooter = null,
  eyebrow = 'ZedReq',
}) {
  const mainClass = ['public-subpage-main', mainClassName].filter(Boolean).join(' ')

  return (
    <MarketingShell mainClassName={mainClass} preFooter={preFooter}>
      <div className="marketing-subpage__content">
        {title ? (
          <header className="public-subpage-hero">
            {eyebrow ? <p className="public-subpage-eyebrow">{eyebrow}</p> : null}
            <h1 className="public-subpage-title">{title}</h1>
          </header>
        ) : null}
        {children}
      </div>
    </MarketingShell>
  )
}
