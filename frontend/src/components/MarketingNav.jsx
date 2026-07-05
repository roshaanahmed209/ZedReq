import React, { useCallback, useEffect, useState } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import FirstPageGlowButton from './FirstPageGlowButton'
import { MARKETING_NAV_ITEMS } from '../constants/marketingNav'

const A = (file) => `${import.meta.env.BASE_URL}assets/${file}`

export default function MarketingNav({ rootRef }) {
  const { theme, setTheme } = useTheme()
  const [menuOpen, setMenuOpen] = useState(false)

  const openMenu = useCallback(() => setMenuOpen(true), [])
  const closeMenu = useCallback(() => setMenuOpen(false), [])

  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => {
      document.body.style.overflow = ''
    }
  }, [menuOpen])

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  useEffect(() => {
    const root = rootRef?.current
    const nav = root?.querySelector('.nav')
    if (!nav) return undefined

    const onNavScroll = () => {
      nav.classList.toggle('nav--scrolled', window.scrollY > 60)
    }
    window.addEventListener('scroll', onNavScroll, { passive: true })
    onNavScroll()
    return () => window.removeEventListener('scroll', onNavScroll)
  }, [rootRef])

  return (
    <>
      <nav className="nav" aria-label="Primary navigation">
        <a href="/" className="nav__brand" aria-label="ZedReq home">
          <img src={A('logo_tr1.svg')} alt="" className="nav__logo" />
          <span className="nav__wordmark">ZedReq</span>
        </a>

        <ul className="nav__links" role="list">
          {MARKETING_NAV_ITEMS.map((item) => (
            <li key={item.label}>
              <a href={item.href} className="nav__link">
                {item.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="nav__actions">
          <button
            type="button"
            className={`nav__theme-btn nav__theme-btn--square${theme === 'dark' ? ' nav__theme-btn--to-light' : ' nav__theme-btn--to-dark'}`}
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            aria-pressed={theme === 'light'}
          >
            {theme === 'dark' ? (
              <svg className="nav__theme-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" strokeWidth="1.6" />
                <path
                  d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                />
              </svg>
            ) : (
              <svg className="nav__theme-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <path fill="currentColor" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
              </svg>
            )}
          </button>
          <button
            type="button"
            className="nav__burger"
            aria-label="Open menu"
            aria-expanded={menuOpen}
            onClick={openMenu}
          >
            <span />
            <span />
            <span />
          </button>
          <FirstPageGlowButton href="/login" className="fp-glow-btn--nav">
            Get Started
          </FirstPageGlowButton>
        </div>
      </nav>

      <div
        className={`nav-overlay${menuOpen ? ' open' : ''}`}
        aria-hidden={!menuOpen}
        role="dialog"
        aria-modal="true"
        aria-label="Site navigation"
      >
        <button
          type="button"
          className="nav-overlay__close btn btn--sm"
          onClick={closeMenu}
          aria-label="Close menu"
        >
          CLOSE ✕
        </button>
        {MARKETING_NAV_ITEMS.map((item) => (
          <a key={item.label} href={item.href} className="nav-overlay__link" onClick={closeMenu}>
            {item.label}
          </a>
        ))}
        <a href="/about" className="nav-overlay__link" onClick={closeMenu}>
          About
        </a>
        <a href="/blogs" className="nav-overlay__link" onClick={closeMenu}>
          Blog
        </a>
        <FirstPageGlowButton href="/login" className="nav-overlay__cta" onClick={closeMenu}>
          Get Started
        </FirstPageGlowButton>
      </div>
    </>
  )
}
