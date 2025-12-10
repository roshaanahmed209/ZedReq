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
      const response = await api.get('/api/user')
      if (response.data && !response.data.error) {
        setUser(response.data)
      }
    } catch (error) {
      console.log('Not authenticated')
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await api.post('/login', { username, password })
      if (response.data.success) {
        await checkAuthStatus()
        return { success: true, message: response.data.message }
      }
      return { success: false, message: response.data.message }
    } catch (error) {
      return { success: false, message: 'Network error. Please try again.' }
    }
  }

  const register = async (userData) => {
    try {
      const response = await api.post('/register', userData)
      if (response.data.success) {
        await checkAuthStatus()
        return { success: true, message: response.data.message }
      }
      return { success: false, message: response.data.message }
    } catch (error) {
      return { success: false, message: 'Network error. Please try again.' }
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

  const value = {
    user,
    login,
    register,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
