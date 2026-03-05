import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import '../css/components/ProtectedRoute.css'

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="protected-route-loading">
        Loading...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/landing" replace />
  }

  return children
}

export default ProtectedRoute
