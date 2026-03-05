import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI, tokenService, NotificationWebSocket } from '../services/api'

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
  const [notificationWs, setNotificationWs] = useState(null)
  const [unreadNotifications, setUnreadNotifications] = useState(0)

  useEffect(() => {
    checkAuthStatus()
    
    // Listen for unauthorized events (token expired, etc.)
    const handleUnauthorized = () => {
      setUser(null)
      tokenService.clearTokens()
    }
    
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized)
    }
  }, [])

  // Connect to WebSocket when user is authenticated
  useEffect(() => {
    if (user && tokenService.isAuthenticated()) {
      const ws = new NotificationWebSocket(
        (notification) => {
          // Handle incoming notification
          console.log('Received notification:', notification)
          setUnreadNotifications(prev => prev + 1)
          // You can dispatch a custom event or use a state manager here
          window.dispatchEvent(new CustomEvent('notification:received', { detail: notification }))
        },
        (error) => {
          console.error('WebSocket error:', error)
        }
      )
      ws.connect()
      setNotificationWs(ws)
      
      // Ping every 30 seconds to keep connection alive
      const pingInterval = setInterval(() => ws.ping(), 30000)
      
      return () => {
        clearInterval(pingInterval)
        ws.disconnect()
      }
    }
  }, [user])

  const checkAuthStatus = async () => {
    try {
      // Check if we have a token
      if (!tokenService.isAuthenticated()) {
        setUser(null)
        setLoading(false)
        return
      }
      
      // Verify token by getting current user
      const response = await authAPI.getCurrentUser()
      if (response.data) {
        setUser(response.data)
      } else {
        setUser(null)
        tokenService.clearTokens()
      }
    } catch (error) {
      // Token invalid or expired
      console.log('Not authenticated or token expired')
      setUser(null)
      tokenService.clearTokens()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password)
      
      // Check if 2FA is required
      if (response.data && response.data.requires_2fa) {
        return {
          success: false,
          requires2FA: true,
          tempToken: response.data.temp_token,
          message: response.data.message || 'Please enter your 2FA code'
        }
      }
      
      if (response.data && response.data.user) {
        setUser(response.data.user)
        return { 
          success: true, 
          message: 'Login successful' 
        }
      }
      
      return { 
        success: false, 
        message: 'Login failed' 
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Network error. Please try again.'
      return { success: false, message: errorMessage }
    }
  }

  const verify2FA = async (tempToken, code) => {
    try {
      const response = await authAPI.verify2FA(tempToken, code)
      
      if (response.data && response.data.user) {
        setUser(response.data.user)
        return { 
          success: true, 
          message: 'Login successful' 
        }
      }
      
      return { 
        success: false, 
        message: '2FA verification failed' 
      }
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '2FA verification failed' 
      }
    }
  }

  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      
      if (response.data && response.data.user) {
        setUser(response.data.user)
        return { 
          success: true, 
          message: 'Registration successful' 
        }
      }
      
      return { 
        success: false, 
        message: 'Registration failed'
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Network error. Please try again.'
      return { success: false, message: errorMessage }
    }
  }

  const logout = async () => {
    try {
      // Disconnect WebSocket
      if (notificationWs) {
        notificationWs.disconnect()
        setNotificationWs(null)
      }
      
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setUnreadNotifications(0)
    }
  }

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }))
  }

  const value = {
    user,
    login,
    verify2FA,
    register,
    logout,
    loading,
    updateUser,
    isAuthenticated: !!user && tokenService.isAuthenticated(),
    checkAuthStatus,
    unreadNotifications,
    setUnreadNotifications
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
