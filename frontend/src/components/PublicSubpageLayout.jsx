import React from 'react'
import { Link } from 'react-router-dom'
import SiteFooter from './SiteFooter'
import '../css/pages/PublicSubpage.css'

export default function PublicSubpageLayout({ title, children, mainClassName = '' }) {
  const mainClass = ['public-subpage-main', mainClassName].filter(Boolean).join(' ')
  return (
    <div className="public-subpage">
      <header className="public-subpage-header">
        <Link to="/" className="public-subpage-logo">ZedReq</Link>
        <nav className="public-subpage-nav">
          <Link to="/">Home</Link>
          <Link to="/get-started">Get started</Link>
        </nav>
      </header>
      <main className={mainClass}>
        {title ? <h1 className="public-subpage-title">{title}</h1> : null}
        {children}
      </main>
      <SiteFooter />
    </div>
  )
}
