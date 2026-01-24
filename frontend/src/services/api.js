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
  getCurrentUser: () => api.get('/api/user'),
  updateProfile: (data) => api.put('/api/user', data),
  searchUsers: (query) => api.get('/api/user/search', { params: { q: query } }),
}

// Post API methods
export const postAPI = {
  createPost: (data) => api.post('/api/posts', data),
  getPost: (postId) => api.get(`/api/posts/${postId}`),
  updatePost: (postId, data) => api.put(`/api/posts/${postId}`, data),
  deletePost: (postId) => api.delete(`/api/posts/${postId}`),
  toggleLike: (postId) => api.post(`/api/posts/${postId}/like`),
  getLikes: (postId) => api.get(`/api/posts/${postId}/likes`),
}

// Feed API methods
export const feedAPI = {
  getFeed: (limit = 20, cursor = null) => {
    const params = { limit }
    if (cursor) params.cursor = cursor
    return api.get('/api/feed', { params })
  },
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

// Job API methods
export const jobAPI = {
  // Get all jobs (with optional filters)
  getJobs: (params = {}) =>
    api.get('/api/jobs', { params }),
  
  // Get remote jobs
  getRemoteJobs: (limit = 50, offset = 0) =>
    api.get('/api/jobs/remote', { params: { limit, offset } }),
  
  // Get jobs posted by current user
  getMyPostedJobs: (limit = 50, offset = 0) =>
    api.get('/api/jobs/my-posts', { params: { limit, offset } }),
  
  // Get saved/bookmarked jobs
  getSavedJobs: (limit = 50, offset = 0) =>
    api.get('/api/jobs/saved', { params: { limit, offset } }),
  
  // Get user's job applications
  getMyApplications: (limit = 50, offset = 0) =>
    api.get('/api/jobs/applications', { params: { limit, offset } }),
  
  // Get a specific job by ID
  getJob: (jobId) =>
    api.get(`/api/jobs/${jobId}`),
  
  // Create a new job posting
  createJob: (jobData) =>
    api.post('/api/jobs', jobData),
  
  // Update a job posting
  updateJob: (jobId, jobData) =>
    api.put(`/api/jobs/${jobId}`, jobData),
  
  // Close a job posting
  closeJob: (jobId) =>
    api.post(`/api/jobs/${jobId}/close`),
  
  // Delete a job posting
  deleteJob: (jobId) =>
    api.delete(`/api/jobs/${jobId}`),
  
  // Apply to a job
  applyToJob: (jobId, applicationData = {}) =>
    api.post(`/api/jobs/${jobId}/apply`, { job_id: jobId, ...applicationData }),
  
  // Get applicants for a job (poster only)
  getJobApplicants: (jobId, limit = 100, offset = 0) =>
    api.get(`/api/jobs/${jobId}/applicants`, { params: { limit, offset } }),
  
  // Update application status (poster only)
  updateApplicationStatus: (applicationId, status) =>
    api.put(`/api/jobs/applications/${applicationId}/status`, { status }),
  
  // Withdraw application
  withdrawApplication: (applicationId) =>
    api.delete(`/api/jobs/applications/${applicationId}`),
  
  // Toggle save/bookmark job
  toggleSaveJob: (jobId) =>
    api.post(`/api/jobs/${jobId}/save`),
  
  // Search jobs
  searchJobs: (query, filters = {}) =>
    api.get('/api/jobs', { params: { query, ...filters } }),
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
    
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    const wsUrl = apiUrl
      .replace('http://', 'ws://')
      .replace('https://', 'wss://')
    
    const fullWsUrl = `${wsUrl}/ws/notifications?token=${token}`
    console.log('Connecting to WebSocket:', fullWsUrl)
    
    try {
      this.ws = new WebSocket(fullWsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected successfully to:', this.ws?.url || fullWsUrl)
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          // Ignore pong messages (keepalive responses)
          if (data.type === 'pong') {
            return
          }
          if (data.type === 'notification' && this.onNotification) {
            this.onNotification(data)
          }
        } catch (e) {
          // Ignore non-JSON messages (legacy pong, etc.)
          if (event.data !== 'pong') {
            console.error('Failed to parse WebSocket message:', e)
          }
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        console.error('WebSocket URL:', this.ws?.url || fullWsUrl)
        console.error('WebSocket readyState:', this.ws?.readyState)
        console.error('WebSocket state:', this.ws ? {
          CONNECTING: this.ws.CONNECTING,
          OPEN: this.ws.OPEN,
          CLOSING: this.ws.CLOSING,
          CLOSED: this.ws.CLOSED,
          current: this.ws.readyState
        } : 'WebSocket is null')
        if (this.onError) this.onError(error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      if (this.onError) this.onError(error)
    }
    
    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        url: this.ws?.url
      })
      
      // Don't reconnect if it was an authentication error (4001)
      if (event.code === 4001) {
        console.error('WebSocket authentication failed - not reconnecting')
        return
      }
      
      // Attempt to reconnect if not intentionally closed
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        console.log(`Attempting to reconnect WebSocket (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
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
