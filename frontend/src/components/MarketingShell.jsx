import React, { useEffect, useRef } from 'react'
import { useTheme } from '../contexts/ThemeContext'
import DarkVeil from './DarkVeil'
import MarketingNav from './MarketingNav'
import MarketingFooter from './MarketingFooter'
import '../css/pages/FirstPage.css'

export default function MarketingShell({
  children,
  className = '',
  mainClassName = '',
  preFooter = null,
  showVeil = true,
}) {
  const rootRef = useRef(null)
  const { theme } = useTheme()

  useEffect(() => {
    const progressEl = document.querySelector('.scroll-progress')
    if (!progressEl) return undefined

    const onProgress = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight
      const pct = max > 0 ? (window.scrollY / max) * 100 : 0
      progressEl.style.width = `${pct}%`
    }
    window.addEventListener('scroll', onProgress, { passive: true })
    onProgress()
    return () => window.removeEventListener('scroll', onProgress)
  }, [])

  const rootClass = ['zedreq-root', 'marketing-subpage', className].filter(Boolean).join(' ')
  const mainClass = ['marketing-subpage__main', mainClassName].filter(Boolean).join(' ')

  return (
    <div className={rootClass} ref={rootRef}>
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <div className="scroll-progress" aria-hidden="true" />
      <MarketingNav rootRef={rootRef} />
      <main id="main" className={mainClass}>
        {showVeil ? (
          <div className="marketing-subpage__veil" aria-hidden="true">
            <DarkVeil
              hueShift={399}
              noiseIntensity={0}
              scanlineIntensity={0.2}
              speed={0.8}
              scanlineFrequency={0}
              warpAmount={1}
              resolutionScale={1}
              forLightBackground={theme === 'light'}
            />
          </div>
        ) : null}
        {children}
      </main>
      {preFooter ? <div className="marketing-subpage__prefooter">{preFooter}</div> : null}
      <MarketingFooter />
    </div>
  )
}
