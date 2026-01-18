import axios from 'axios'

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Token management functions
export const tokenService = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  },
  
  clearTokens: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
  
  isAuthenticated: () => !!localStorage.getItem(ACCESS_TOKEN_KEY),
}

// Request interceptor - add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = tokenService.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Handle specific error codes
    if (error.response) {
      const { status } = error.response
      
      // Log error for debugging
      console.error('API Error:', {
        status,
        url: error.config?.url,
        message: error.response?.data?.detail || error.response?.data?.message
      })
      
      // Handle 401 Unauthorized - try to refresh token
      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        
        const refreshToken = tokenService.getRefreshToken()
        if (refreshToken) {
          try {
            const response = await axios.post(
              `${api.defaults.baseURL}/api/auth/refresh`,
              { refresh_token: refreshToken }
            )
            
            const { access_token, refresh_token } = response.data
            tokenService.setTokens(access_token, refresh_token)
            
            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return api(originalRequest)
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            tokenService.clearTokens()
            window.dispatchEvent(new CustomEvent('auth:unauthorized'))
          }
        } else {
          // No refresh token, trigger logout
          window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        }
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API methods (JWT-based)
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/api/auth/login', { username, password })
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData)
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  logout: () => {
    tokenService.clearTokens()
    return Promise.resolve()
  },
  
  getCurrentUser: () => api.get('/api/auth/me'),
  
  refreshToken: async () => {
    const refreshToken = tokenService.getRefreshToken()
    if (!refreshToken) throw new Error('No refresh token')
    
    const response = await api.post('/api/auth/refresh', { refresh_token: refreshToken })
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  isAuthenticated: () => tokenService.isAuthenticated(),
}

// User API methods
export const userAPI = {
  getCurrentUser: () => api.get('/api/auth/me'),
  updateProfile: (data) => api.put('/api/user', data),
  searchUsers: (query) => api.get('/api/users/search', { params: { q: query } }),
}

// Network API methods
export const networkAPI = {
  // Discover new users (20% of user base)
  discoverUsers: (limit = 20) => 
    api.get('/api/network/discover', { params: { limit } }),
  
  // Get friend-of-friend suggestions
  getSuggestions: (limit = 20) => 
    api.get('/api/network/suggestions', { params: { limit } }),
  
  // Get current user's connections
  getConnections: () => 
    api.get('/api/network/connections'),
}

// Connection Request API methods
export const connectionAPI = {
  // Send connection request to a user
  sendRequest: (userUuid, message = null) => 
    api.post(`/api/connections/request/${userUuid}`, message ? { message } : {}),
  
  // Accept a connection request
  acceptRequest: (requestId) => 
    api.put(`/api/connections/accept/${requestId}`),
  
  // Reject a connection request
  rejectRequest: (requestId) => 
    api.put(`/api/connections/reject/${requestId}`),
  
  // Remove an existing connection
  removeConnection: (connectionId) => 
    api.delete(`/api/connections/${connectionId}`),
  
  // Get pending requests received
  getPendingRequests: () => 
    api.get('/api/connections/pending'),
  
  // Get sent requests
  getSentRequests: () => 
    api.get('/api/connections/sent'),
}

// Notification API methods
export const notificationAPI = {
  // Get all notifications
  getNotifications: (limit = 50, offset = 0, unreadOnly = false) => 
    api.get('/api/notifications', { params: { limit, offset, unread_only: unreadOnly } }),
  
  // Get unread count
  getUnreadCount: () => 
    api.get('/api/notifications/unread/count'),
  
  // Mark notification as read
  markAsRead: (notificationId) => 
    api.put(`/api/notifications/${notificationId}/read`),
  
  // Mark all as read
  markAllAsRead: () => 
    api.put('/api/notifications/read-all'),
}

// WebSocket connection for real-time notifications
export class NotificationWebSocket {
  constructor(onNotification, onError = null) {
    this.ws = null
    this.onNotification = onNotification
    this.onError = onError
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }
  
  connect() {
    const token = tokenService.getAccessToken()
    if (!token) {
      console.error('No token available for WebSocket connection')
      return
    }
    
    const wsUrl = (import.meta.env.VITE_API_URL || 'http://localhost:5000')
      .replace('http://', 'ws://')
      .replace('https://', 'wss://')
    
    this.ws = new WebSocket(`${wsUrl}/ws/notifications?token=${token}`)
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'notification' && this.onNotification) {
          this.onNotification(data)
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (this.onError) this.onError(error)
    }
    
    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code)
      
      // Attempt to reconnect if not intentionally closed
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
      }
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close(1000) // Normal closure
      this.ws = null
    }
  }
  
  // Send ping to keep connection alive
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send('ping')
    }
  }
}

export default api
