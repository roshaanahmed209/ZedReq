import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('admin_token')
    const storedAdmin = localStorage.getItem('admin_user')
    
    if (token && storedAdmin) {
      try {
        setAdmin(JSON.parse(storedAdmin))
        setIsAuthenticated(true)
        // Verify token is still valid
        verifyAuth()
      } catch (e) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_user')
      }
    }
    setLoading(false)
  }, [])

  const verifyAuth = async () => {
    try {
      const response = await authAPI.getMe()
      setAdmin(response.data)
      setIsAuthenticated(true)
      localStorage.setItem('admin_user', JSON.stringify(response.data))
    } catch (error) {
      logout()
    }
  }

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password)
      const { admin: adminData, access_token } = response.data
      
      localStorage.setItem('admin_token', access_token)
      localStorage.setItem('admin_user', JSON.stringify(adminData))
      
      setAdmin(adminData)
      setIsAuthenticated(true)
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    setAdmin(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        admin,
        loading,
        isAuthenticated,
        login,
        logout,
        verifyAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
