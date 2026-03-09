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
  timeout: 150000, // 150 second default timeout (increased for LLM and complex queries)
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
          message: error.response?.data?.detail || error.response?.data?.message || error.response?.data?.error
        })
        
        // Handle rate limiting (429)
        if (status === 429) {
          const retryAfter = error.response.headers?.['retry-after'] || error.response.headers?.['Retry-After'] || 60
          const rateLimitInfo = error.response.data?.detail || error.response.data?.message
          
          // Enhance error object with rate limit info
          error.rateLimitInfo = {
            retryAfter: parseInt(retryAfter),
            remaining: error.response.data?.remaining || 0,
            limit: error.response.headers?.['x-ratelimit-limit'] || error.response.headers?.['X-RateLimit-Limit'] || null,
            message: rateLimitInfo
          }
        }
      
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
    // Check if 2FA is required
    if (response.data.requires_2fa) {
      // Return temp token for 2FA verification
      return response
    }
    // Normal login - set tokens
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  verify2FA: async (tempToken, code) => {
    const response = await api.post('/api/auth/2fa/verify', { 
      temp_token: tempToken, 
      code: code 
    })
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
  
  logout: async () => {
    try {
      // Call backend logout endpoint to trigger context refresh
      await api.post('/api/auth/logout')
    } catch (error) {
      // Don't fail logout if backend call fails
      console.warn('Backend logout call failed:', error)
    } finally {
      // Always clear tokens locally
      tokenService.clearTokens()
    }
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
  getUserProfile: (userId) => api.get(`/api/user/${userId}`),
  updateProfile: (data) => api.put('/api/user', data),
  searchUsers: (query) => api.get('/api/user/search', { params: { q: query } }),
  getConnectionCounts: (userId) => api.get(`/api/user/${userId}/connections/count`),
  getUserCertificates: (userId) => api.get(`/api/user/${userId}/certificates`),
  // Subscription & quota usage
  getSubscriptionUsage: () => api.get('/api/user/subscription/usage'),
}

// Profile Features API methods
export const profileFeaturesAPI = {
  // Experience
  getExperiences: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/experience/${userId}`, { params: { limit, offset } }),
  createExperience: (data) => api.post('/api/profile/experience', data),
  updateExperience: (experienceId, data) => api.put(`/api/profile/experience/${experienceId}`, data),
  deleteExperience: (experienceId) => api.delete(`/api/profile/experience/${experienceId}`),
  
  // Education
  getEducations: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/education/${userId}`, { params: { limit, offset } }),
  createEducation: (data) => api.post('/api/profile/education', data),
  updateEducation: (educationId, data) => api.put(`/api/profile/education/${educationId}`, data),
  deleteEducation: (educationId) => api.delete(`/api/profile/education/${educationId}`),
  
  // Projects
  getProjects: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/projects/${userId}`, { params: { limit, offset } }),
  createProject: (data) => api.post('/api/profile/projects', data),
  updateProject: (projectId, data) => api.put(`/api/profile/projects/${projectId}`, data),
  deleteProject: (projectId) => api.delete(`/api/profile/projects/${projectId}`),
  
  // Recommendations
  getRecommendations: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/recommendations/${userId}`, { params: { limit, offset } }),
  createRecommendation: (data) => api.post('/api/profile/recommendations', data),
  updateRecommendation: (recommendationId, data) => api.put(`/api/profile/recommendations/${recommendationId}`, data),
  deleteRecommendation: (recommendationId) => api.delete(`/api/profile/recommendations/${recommendationId}`),
  
  // Interests
  getInterests: (userId, interestType = null, limit = 50, offset = 0) => {
    const params = { limit, offset }
    if (interestType) params.interest_type = interestType
    return api.get(`/api/profile/interests/${userId}`, { params })
  },
  createInterest: (data) => api.post('/api/profile/interests', data),
  updateInterest: (interestId, data) => api.put(`/api/profile/interests/${interestId}`, data),
  deleteInterest: (interestId) => api.delete(`/api/profile/interests/${interestId}`),
  
  // Analytics
  getAnalytics: (userId, days = 30) => api.get(`/api/profile/analytics/${userId}`, { params: { days } }),
  getProfileViews: (userId, days = 30) => api.get(`/api/profile/analytics/${userId}/views`, { params: { days } }),
  trackProfileView: (userId, source = 'direct') => api.post('/api/profile/analytics/track-view', { user_id: userId, source }),
}

// Post API methods
export const postAPI = {
  createPost: (data) => api.post('/api/posts', data),
  getPost: (postId) => api.get(`/api/posts/${postId}`),
  getUserPosts: (userId, params = {}) => api.get(`/api/posts/user/${userId}`, { params }),
  getUserFeaturedPosts: (userId, params = {}) => {
    // Support both object and number for backward compatibility
    if (typeof params === 'number') {
      return api.get(`/api/posts/user/${userId}/featured`, { params: { limit: params, offset: 0 } })
    }
    return api.get(`/api/posts/user/${userId}/featured`, { params })
  },
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
  sendRequest: (userUuid, message = null) => {
    // Always send an object, even if message is null/undefined
    const payload = message ? { message } : {};
    return api.post(`/api/connections/request/${userUuid}`, payload);
  },
  
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
  
  // Get personalized job recommendations
  getJobRecommendations: (userId, limit = 10) =>
    api.get(`/api/jobs/recommendations/${userId}`, { params: { limit } }),
  
  // Get interview recommendations (jobs with attempt counts)
  getInterviewRecommendations: (userId, limit = 10) =>
    api.get(`/api/interviews/recommendations/${userId}`, { params: { limit } }),
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

// Messaging API methods
export const messagingAPI = {
  // Get all conversations for current user
  getConversations: () => 
    api.get('/api/messaging/conversations'),
  
  // Get messages with a specific user
  getMessages: (recipientId, limit = 50) => 
    api.get(`/api/messaging/messages/${recipientId}`, { params: { limit } }),
  
  // Send a message
  sendMessage: (recipientId, content, messageType = 'text') => 
    api.post('/api/messaging/messages', {
      recipient_id: recipientId,
      content,
      message_type: messageType
    }),
  
  // Mark conversation as read
  markConversationRead: (recipientId) => 
    api.post(`/api/messaging/messages/${recipientId}/read`),
}

// LMS API methods
export const lmsAPI = {
  // Course endpoints
  getCourses: (params = {}) =>
    api.get('/api/lms/courses', { params }),
  
  getCourse: (courseId) =>
    api.get(`/api/lms/courses/${courseId}`),
  
  createCourse: (courseData) =>
    api.post('/api/lms/courses', courseData),
  
  updateCourse: (courseId, courseData) =>
    api.put(`/api/lms/courses/${courseId}`, courseData),
  
  getCourseSections: (courseId) =>
    api.get(`/api/lms/courses/${courseId}/sections`),
  
  getCourseResources: (courseId) =>
    api.get(`/api/lms/courses/${courseId}/resources`),
  
  // User course endpoints
  enrollInCourse: (courseId) =>
    api.post(`/api/lms/courses/${courseId}/enroll`),
  
  getMyCourses: (params = {}) =>
    api.get('/api/lms/my-courses', { params, timeout: 150000 }), // 150 seconds - critical endpoint
  
  getMyCourse: (courseId) =>
    api.get(`/api/lms/my-courses/${courseId}`, { timeout: 45000 }),
  
  updateCourseProgress: (courseId, progress) =>
    api.put(`/api/lms/my-courses/${courseId}/progress`, { progress }),
  
  // Dashboard endpoints
  getDashboard: () =>
    api.get('/api/lms/dashboard', { timeout: 150000 }), // 150 seconds for complex queries
  
  getWeeklyPerformance: (days = 7) =>
    api.get('/api/lms/dashboard/weekly', { params: { days }, timeout: 150000 }), // 150 seconds
  
  getDomainPerformance: () =>
    api.get('/api/lms/dashboard/domains', { timeout: 150000 }), // 150 seconds
  
  // Question/Answer endpoints
  getCourseQuestions: (courseId, sectionId = null) => {
    const params = sectionId ? { section_id: sectionId } : {}
    return api.get(`/api/lms/courses/${courseId}/questions`, { params })
  },
  
  getQuestion: (questionId) =>
    api.get(`/api/lms/questions/${questionId}`),
  
  createQuestion: (questionData) =>
    api.post('/api/lms/questions', questionData),
  
  submitAnswer: (questionId, answerText) =>
    api.post(`/api/lms/questions/${questionId}/answer`, {
      question_id: questionId,
      answer_text: answerText
    }),
  
  evaluateAnswer: (answerId, evaluation) =>
    api.put(`/api/lms/answers/${answerId}/evaluate`, evaluation),
  
  getMyAnswers: (params = {}) =>
    api.get('/api/lms/my-answers', { params }),
  
  // Activity endpoints
  getActivities: (limit = 10) =>
    api.get('/api/lms/activities', { params: { limit }, timeout: 150000 }), // 150 seconds
  
  // Recommendation endpoints
  getRecommendations: (limit = 5) =>
    api.get('/api/lms/recommendations', { params: { limit }, timeout: 150000 }), // 150 seconds
  
  dismissRecommendation: (recommendationId) =>
    api.post(`/api/lms/recommendations/${recommendationId}/dismiss`),
  
  // Deadline endpoints
  getDeadlines: (limit = 10) =>
    api.get('/api/lms/deadlines', { params: { limit }, timeout: 150000 }), // 150 seconds
  
  createDeadline: (deadlineData) =>
    api.post('/api/lms/deadlines', deadlineData),
  
  completeDeadline: (deadlineId) =>
    api.put(`/api/lms/deadlines/${deadlineId}/complete`),
  
  // Certificate endpoints
  getCertificates: () =>
    api.get('/api/lms/certificates', { timeout: 150000 }), // 150 seconds
  
  getCertificateByNumber: (certificateNumber) =>
    api.get(`/api/lms/certificates/${certificateNumber}`),
  
  // Section progress endpoints
  getSectionProgress: (sectionId) =>
    api.get(`/api/lms/sections/${sectionId}/progress`),
  
  updateSectionProgress: (sectionId, progressData) =>
    api.put(`/api/lms/sections/${sectionId}/progress`, progressData),
  
  // Azel Agent endpoints (longer timeout for web searches and LLM calls)
  triggerAzelProcessCourse: (courseId) =>
    api.post(`/api/lms/azel/process-course/${courseId}`, {}, { timeout: 150000 }), // 150 seconds timeout
  
  // Course performance endpoint
  getCoursePerformance: (courseId) =>
    api.get(`/api/lms/dashboard/courses/${courseId}`, { timeout: 150000 }), // 150 seconds
  
  // Seez Agent endpoints (longer timeout for LLM evaluation calls)
  triggerSeezEvaluateCourse: (courseId) =>
    api.post(`/api/lms/seez/evaluate-course/${courseId}`, {}, { timeout: 150000 }), // 150 seconds timeout
  
  triggerSeezEvaluateAnswers: (answerIds) =>
    api.post('/api/lms/seez/evaluate-answers', answerIds, { timeout: 150000 }), // 150 seconds timeout

    // Course Recommendation endpoints
    generateRecommendations: (limit = 5) =>
      api.post(`/api/lms/generate-recommendations?limit=${limit}`, {}, { timeout: 150000 }), // 150 seconds timeout
  }

// Nemz API methods
export const nemzAPI = {
  chat: ({ message, sessionId }) =>
    api.post('/api/nemz/chat', { message, session_id: sessionId }),
  
  deleteSession: (sessionId) =>
    api.delete(`/api/nemz/chat/session/${sessionId}`),
  
  searchAll: ({ query, searchType, limit = 10 }) =>
    api.post('/api/nemz/search', { query, search_type: searchType, limit }),
  
  searchJobs: ({ query, limit = 10 }) =>
    api.post('/api/nemz/search/jobs', { query, limit }),
  
  searchProfiles: ({ query, limit = 10 }) =>
    api.post('/api/nemz/search/profiles', { query, limit }),
  
  searchPosts: ({ query, limit = 10 }) =>
    api.post('/api/nemz/search/posts', { query, limit }),
}

// Vec API methods (Vector Database Sync)
export const vecAPI = {
  sync: (force = false) =>
    api.post('/api/vec/sync', { force }, { timeout: 300000 }), // 5 minutes timeout
  
  syncBackground: (force = false) =>
    api.post('/api/vec/sync/background', { force }, { timeout: 30000 }),
  
  getStatus: () =>
    api.get('/api/vec/status', { timeout: 30000 }),
}

// Interview API methods
export const interviewAPI = {
  startInterview: (jobId) =>
    api.post('/api/interviews/start', { job_id: jobId }),
  
  getInterview: (interviewId) =>
    api.get(`/api/interviews/${interviewId}`),
  
  completeInterview: (interviewId) =>
    api.post(`/api/interviews/${interviewId}/complete`),
  
  getMyInterviews: ({ jobId } = {}) => {
    const params = jobId ? { job_id: jobId } : {}
    return api.get('/api/interviews/my-interviews', { params })
  },
  
  getInterviewRizFeedback: (interviewId) =>
    api.get(`/api/interviews/${interviewId}/riz-feedback`),
  
  refreshRizFeedback: (interviewId) =>
    api.post(`/api/interviews/${interviewId}/riz-feedback/refresh`),
}

// Context API methods - Generic context update endpoint
export const contextAPI = {
  /**
   * Update user context based on actions
   * @param {string} action - Action type: "apply" | "like" | "view"
   * @param {string} entityType - Entity type: "job" | "post" | "profile"
   * @param {number} entityId - Entity ID
   * @returns {Promise} API response
   */
  updateContext: async (action, entityType, entityId) => {
    try {
      const response = await api.post('/api/context/update', {
        action,
        entity_type: entityType,
        entity_id: entityId
      })
      return response
    } catch (error) {
      // Silently fail - context updates are non-critical
      console.warn('Context update failed:', error)
      return { data: { success: false } }
    }
  }
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

// WebSocket connection for real-time messaging
export class MessagingWebSocket {
  constructor(onMessage, onError = null) {
    this.ws = null
    this.onMessage = onMessage
    this.onError = onError
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.pingInterval = null
  }
  
  connect() {
    const token = tokenService.getAccessToken()
    if (!token) {
      console.error('No token available for messaging WebSocket connection')
      return
    }
    
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    const wsUrl = apiUrl
      .replace('http://', 'ws://')
      .replace('https://', 'wss://')
    
    const fullWsUrl = `${wsUrl}/api/messaging/messages?token=${token}`
    console.log('Connecting to Messaging WebSocket:', fullWsUrl)
    
    try {
      this.ws = new WebSocket(fullWsUrl)
      
      this.ws.onopen = () => {
        console.log('Messaging WebSocket connected successfully')
        this.reconnectAttempts = 0
        
        // Start ping interval to keep connection alive
        this.pingInterval = setInterval(() => this.ping(), 30000)
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Handle pong responses
          if (data.type === 'pong') {
            return
          }
          
          // Handle connection confirmation
          if (data.type === 'connected') {
            console.log('Messaging WebSocket connected:', data.message)
            return
          }
          
          // Handle new messages
          if (data.type === 'new_message' && this.onMessage) {
            this.onMessage(data.message)
          }
          
          // Handle message sent confirmation
          if (data.type === 'message_sent' && this.onMessage) {
            this.onMessage(data.message)
          }
          
          // Handle messages list
          if (data.type === 'messages' && this.onMessage) {
            this.onMessage({ type: 'messages_list', ...data })
          }
          
          // Handle errors
          if (data.type === 'error') {
            // Only log detailed errors in development
            if (import.meta.env.DEV) {
              console.error('Messaging WebSocket error:', data.message)
            }
            if (this.onError) {
              this.onError(new Error(data.message))
            }
          }
        } catch (e) {
          if (event.data !== 'pong') {
            console.error('Failed to parse messaging WebSocket message:', e)
          }
        }
      }
      
      this.ws.onerror = (error) => {
        // Only log detailed errors in development to reduce console noise
        if (import.meta.env.DEV) {
          console.error('Messaging WebSocket error:', error)
          console.error('WebSocket state:', this.ws?.readyState)
          console.error('WebSocket URL:', this.ws?.url || fullWsUrl)
        }
        
        // Don't call onError for connection failures - let onclose handle reconnection
        // The onclose handler will manage reconnection logic
      }
      
      this.ws.onclose = (event) => {
        // Only log in development to reduce console noise
        if (import.meta.env.DEV) {
          console.log('Messaging WebSocket closed:', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean,
            url: this.ws?.url
          })
        }
        
        // Clear ping interval
        if (this.pingInterval) {
          clearInterval(this.pingInterval)
          this.pingInterval = null
        }
        
        // Don't reconnect if authentication error
        if (event.code === 4001) {
          if (import.meta.env.DEV) {
            console.error('Messaging WebSocket authentication failed - not reconnecting')
          }
          if (this.onError) {
            this.onError(new Error('Authentication failed. Please log in again.'))
          }
          return
        }
        
        // Don't reconnect if manually closed (code 1000)
        if (event.wasClean && event.code === 1000) {
          if (import.meta.env.DEV) {
            console.log('Messaging WebSocket closed normally')
          }
          return
        }
        
        // Handle connection failures (code 1006) - server unreachable
        if (event.code === 1006) {
          if (import.meta.env.DEV) {
            console.warn('Messaging WebSocket connection failed. Server may be unreachable.')
          }
          // Still attempt reconnection but with longer delay
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            this.reconnectDelay = Math.min(this.reconnectDelay * 2, 60000) // Max 60s for server issues
            setTimeout(() => this.connect(), this.reconnectDelay)
          }
          return
        }
        
        // Attempt to reconnect for other errors
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          if (import.meta.env.DEV) {
            console.log(`Attempting to reconnect Messaging WebSocket (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
          }
          setTimeout(() => this.connect(), this.reconnectDelay)
          this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000) // Exponential backoff, max 30s
        } else {
          if (import.meta.env.DEV) {
            console.error('Max reconnection attempts reached for Messaging WebSocket')
          }
          if (this.onError) {
            this.onError(new Error('Failed to connect to messaging server after multiple attempts. Please check if the backend is running.'))
          }
        }
      }
    } catch (error) {
      console.error('Failed to create Messaging WebSocket:', error)
      if (this.onError) this.onError(error)
    }
  }
  
  disconnect() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
    if (this.ws) {
      this.ws.close(1000) // Normal closure
      this.ws = null
    }
  }
  
  // Send ping to keep connection alive
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'ping' }))
    }
  }
  
  // Send a message
  sendMessage(recipientId, content, messageType = 'text') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'send_message',
        recipient_id: recipientId,
        content,
        message_type: messageType
      }))
    } else {
      console.error('WebSocket is not open. Cannot send message.')
    }
  }
  
  // Get messages for a conversation
  getMessages(recipientId, limit = 50) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'get_messages',
        recipient_id: recipientId,
        limit
      }))
    } else {
      console.error('WebSocket is not open. Cannot get messages.')
    }
  }
  
  // Mark conversation as read
  markRead(recipientId, messageId = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'mark_read',
        recipient_id: recipientId,
        message_id: messageId
      }))
    } else {
      console.error('WebSocket is not open. Cannot mark as read.')
    }
  }
}

export default api
