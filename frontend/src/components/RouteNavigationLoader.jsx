import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import AppLoader from './AppLoader'

const DISPLAY_MS = 360

/**
 * Shown briefly when `location.pathname` changes so in-flight navigations
 * match light/dark theme (same CSS variables as the rest of the app).
 */
export default function RouteNavigationLoader() {
  const location = useLocation()
  const [visible, setVisible] = useState(false)
  const prevPathname = useRef(null)

  useEffect(() => {
    const prev = prevPathname.current
    prevPathname.current = location.pathname
    if (prev === null) return
    if (prev === location.pathname) return

    setVisible(true)
    const id = window.setTimeout(() => setVisible(false), DISPLAY_MS)
    return () => {
      window.clearTimeout(id)
      setVisible(false)
    }
  }, [location.pathname])

  if (!visible) return null

  return <AppLoader variant="overlay" label="Loading" />
}
