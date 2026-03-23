import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI, tokenService, NotificationWebSocket } from '../services/api'

const AuthContext = createContext()

const SESSION_FEED_STATS_KEY = 'zedreq_session_feed_stats'

function randomFeedStats() {
  return {
    profileViews: Math.floor(Math.random() * 200),
    postImpressions: Math.floor(Math.random() * 800),
  }
}

function readStoredFeedStats(userId) {
  if (userId == null) return null
  try {
    const raw = sessionStorage.getItem(SESSION_FEED_STATS_KEY)
    if (!raw) return null
    const o = JSON.parse(raw)
    if (String(o.userId) !== String(userId)) return null
    return {
      profileViews: o.profileViews,
      postImpressions: o.postImpressions,
    }
  } catch {
    return null
  }
}

function writeStoredFeedStats(userId, stats) {
  if (userId == null) return
  sessionStorage.setItem(
    SESSION_FEED_STATS_KEY,
    JSON.stringify({ userId, ...stats })
  )
}

function clearStoredFeedStats() {
  sessionStorage.removeItem(SESSION_FEED_STATS_KEY)
}

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
  const [sessionFeedStats, setSessionFeedStats] = useState(null)

  useEffect(() => {
    checkAuthStatus()
    
    // Listen for unauthorized events (token expired, etc.)
    const handleUnauthorized = () => {
      setUser(null)
      setSessionFeedStats(null)
      clearStoredFeedStats()
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

  const hydrateSessionFeedStats = (userId) => {
    const id = userId
    if (id == null) return
    const existing = readStoredFeedStats(id)
    if (existing) {
      setSessionFeedStats(existing)
      return
    }
    const stats = randomFeedStats()
    writeStoredFeedStats(id, stats)
    setSessionFeedStats(stats)
  }

  const refreshSessionFeedStats = (userId) => {
    const id = userId
    if (id == null) return
    const stats = randomFeedStats()
    writeStoredFeedStats(id, stats)
    setSessionFeedStats(stats)
  }

  const checkAuthStatus = async () => {
    try {
      // Check if we have a token
      if (!tokenService.isAuthenticated()) {
        setUser(null)
        setSessionFeedStats(null)
        setLoading(false)
        return
      }
      
      // Verify token by getting current user
      const response = await authAPI.getCurrentUser()
      if (response.data) {
        const userData = response.data
        setUser(userData)
        hydrateSessionFeedStats(userData.id ?? userData.uid)
      } else {
        setUser(null)
        setSessionFeedStats(null)
        tokenService.clearTokens()
      }
    } catch (error) {
      // Token invalid or expired
      console.log('Not authenticated or token expired')
      setUser(null)
      setSessionFeedStats(null)
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
        const u = response.data.user
        setUser(u)
        refreshSessionFeedStats(u.id ?? u.uid)
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
      const noResponse = !error.response
      const looksLikeNetwork =
        noResponse &&
        (error.code === 'ERR_NETWORK' ||
          String(error.message || '').toLowerCase().includes('network'))
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        (looksLikeNetwork
          ? 'Cannot reach the API. Confirm the backend is running, and that VITE_API_URL (or the URL in your browser) matches your CORS settings — localhost and 127.0.0.1 are not interchangeable.'
          : 'Network error. Please try again.')
      return { success: false, message: errorMessage }
    }
  }

  const verify2FA = async (tempToken, code) => {
    try {
      const response = await authAPI.verify2FA(tempToken, code)
      
      if (response.data && response.data.user) {
        const u = response.data.user
        setUser(u)
        refreshSessionFeedStats(u.id ?? u.uid)
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
        const u = response.data.user
        setUser(u)
        refreshSessionFeedStats(u.id ?? u.uid)
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
      const noResponse = !error.response
      const looksLikeNetwork =
        noResponse &&
        (error.code === 'ERR_NETWORK' ||
          String(error.message || '').toLowerCase().includes('network'))
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        (looksLikeNetwork
          ? 'Cannot reach the API. Confirm the backend is running, and that VITE_API_URL (or the URL in your browser) matches your CORS settings — localhost and 127.0.0.1 are not interchangeable.'
          : 'Network error. Please try again.')
      return { success: false, message: errorMessage }
    }
  }

  const logout = () => {
    // Disconnect WebSocket
    if (notificationWs) {
      notificationWs.disconnect()
      setNotificationWs(null)
    }

    // Clear state immediately so the UI reacts instantly
    setUser(null)
    setUnreadNotifications(0)
    setSessionFeedStats(null)
    clearStoredFeedStats()

    // Fire backend logout (context update) in the background — don't await
    authAPI.logout().catch(err => console.warn('Background logout call failed:', err))
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
    setUnreadNotifications,
    sessionFeedStats,
    refreshSessionFeedStats,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
