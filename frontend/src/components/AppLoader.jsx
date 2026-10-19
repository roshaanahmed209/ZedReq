import '../css/components/AppLoader.css'

/**
 * Shared themed loader (Uiverse-style). Use `overlay` for route transitions,
 * `fullscreen` for auth / data gates.
 */
export default function AppLoader({ variant = 'fullscreen', label = 'Loading', className = '' }) {
  const rootClass = ['app-loader', `app-loader--${variant}`, className].filter(Boolean).join(' ')

  return (
    <div className={rootClass} role="status" aria-live="polite" aria-busy="true">
      <div className="app-loader__loader" aria-hidden>
        <div className="app-loader__circle" />
      </div>
      {label ? <span className="app-loader__label">{label}</span> : null}
    </div>
  )
}
