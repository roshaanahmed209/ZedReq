import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      // Use the new session endpoint to check authentication
      const response = await api.get('/session')
      if (response.data && response.data.success && response.data.data) {
        setUser(response.data.data)
      } else {
        setUser(null)
      }
    } catch (error) {
      // Not authenticated or session expired
      console.log('Not authenticated')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await api.post('/login', { username, password })
      
      if (response.data.success) {
        // Set user data from response
        const userData = response.data.data
        setUser(userData)
        return { 
          success: true, 
          message: response.data.message || 'Login successful' 
        }
      }
      
      return { 
        success: false, 
        message: response.data.message || 'Login failed' 
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Network error. Please try again.'
      return { success: false, message: errorMessage }
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/register', userData)
      
      if (response.data.success) {
        // Set user data from response
        const registeredUser = response.data.data
        setUser(registeredUser)
        return { 
          success: true, 
          message: response.data.message || 'Registration successful' 
        }
      }
      
      return { 
        success: false, 
        message: response.data.message || 'Registration failed',
        errors: response.data.errors || []
      }
    } catch (error) {
      const errorMessage = error.response?.data?.message || 'Network error. Please try again.'
      const errors = error.response?.data?.errors || []
      return { success: false, message: errorMessage, errors }
    }
  }

  const logout = async () => {
    try {
      await api.get('/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
    }
  }

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }))
  }

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    updateUser,
    isAuthenticated: !!user,
    checkAuthStatus
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
