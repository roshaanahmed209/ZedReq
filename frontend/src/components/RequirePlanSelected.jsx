import React, { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import '../css/components/ProtectedRoute.css'

const EXEMPT_PATHS = ['/choose-plan', '/checkout', '/enterprise-inquiry']

function pathIsExempt(pathname) {
  return EXEMPT_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`))
}

const RequirePlanSelected = ({ children }) => {
  const { user, loading: authLoading } = useAuth()
  const location = useLocation()
  const [checking, setChecking] = useState(true)
  const [requiresSelection, setRequiresSelection] = useState(false)

  useEffect(() => {
    if (authLoading || !user) {
      return
    }
    if (pathIsExempt(location.pathname)) {
      setRequiresSelection(false)
      setChecking(false)
      return
    }

    setChecking(true)
    let cancelled = false
    ;(async () => {
      try {
        const { data } = await api.get('/api/user/subscription')
        if (!cancelled) {
          setRequiresSelection(Boolean(data?.requires_plan_selection))
        }
      } catch (e) {
        if (!cancelled) {
          setRequiresSelection(true)
        }
      } finally {
        if (!cancelled) {
          setChecking(false)
        }
      }
    })()

    return () => {
      cancelled = true
    }
  }, [user, authLoading, location.pathname])

  if (authLoading || (user && checking)) {
    return (
      <div className="protected-route-loading">
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (pathIsExempt(location.pathname)) {
    return children
  }

  if (requiresSelection) {
    return <Navigate to="/choose-plan" replace />
  }

  return children
}

export default RequirePlanSelected
